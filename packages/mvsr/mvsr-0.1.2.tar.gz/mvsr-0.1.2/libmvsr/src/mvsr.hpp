#ifndef MVSR_HPP
#define MVSR_HPP

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iterator>
#include <memory>

#include "mvsr_heap.hpp"
#include "mvsr_list.hpp"
#include "mvsr_mat.hpp"

/**
 * @brief Segmented Regression object. Uses a greedy algorithm to realize the
 * segmented regression.
 *
 * @tparam Scalar Type of a single value. Must be an arithmetic type.
 */
template <typename Scalar>
class Mvsr
{
public:
    /**
     * @brief Struct to store a single segment. The involved matrices are stored
     * in a variable sized array after the segment itselg (see mvsr_list).
     */
    struct Segment : Heap<Scalar, Segment>::Reference
    {
        size_t sampleSize = 0;
    };

    /**
     * @brief Creates an mvsr object for given from samples in the data parameter.
     *
     * @param dimensions Number of input dimensions.
     * @param variants Number of variants (output functions with shared breakpoints).
     */
    Mvsr(size_t dimensions, size_t variants)
        : dimensions(dimensions), variants(variants), offY(dimensions * dimensions + offX),
          segSize(dimensions * (dimensions + variants) + offX),
          pieces(dimensions * (dimensions + variants) + offX),
          tempMemory(new Scalar[3 * segSize])
    {}

    /**
     * @brief Copy Constructor. Enables a deep copy to save the current state of the regression.
     *
     * @param other Other segmented regression object.
     */
    Mvsr(const Mvsr<Scalar> &other)
        : dimensions(other.dimensions), variants(other.variants),
          offY(other.offY), segSize(other.segSize), pieces(other.pieces),
          tempMemory(new Scalar[3 * dimensions*variants])
    {
        queue = other.queue.copyByOrder(other.pieces, pieces);
    }

    Mvsr(Mvsr &&) = default;
    Mvsr &operator=(Mvsr &&) & = default;
    Mvsr &operator=(const Mvsr &) & = delete;
    ~Mvsr() = default;

    /**
     * @brief Places segments based on samples.
     *
     * @param data        Pointer to value matrix.
     * @param sampleCount Number of Samples.
     * @param minPerSeg   Minimum number of samples per segment.
     */
    void placeSegments(const Scalar *data, size_t sampleCount, size_t minPerSeg)
    {
        pieces.clear();
        queue.reserve(sampleCount / minPerSeg);
        pieces.reserve(sampleCount / minPerSeg);

        const auto rowSize = dimensions + variants;
        const size_t segMatSize = rowSize * minPerSeg;
        data += sampleCount * rowSize;
        segInit(segGetStartPtr(*pieces.prepend(Segment{
                    .sampleSize = minPerSeg + (sampleCount % minPerSeg),
                })),
                minPerSeg + (sampleCount % minPerSeg),
                data -= (minPerSeg + (sampleCount % minPerSeg)) * rowSize);
        sampleCount -= sampleCount % minPerSeg;
        while ((sampleCount -= minPerSeg) != 0)
        {
            segInit(segGetStartPtr(*pieces.prepend(Segment{.sampleSize = minPerSeg})), minPerSeg,
                    data -= segMatSize);
        }
    }

    /**
     * @brief Reduces the number of segments using a greedy approach.
     *
     * @param numSegments Target number of segments.
     */
    void reduceGreedy(size_t numSegments)
    {
        if (numSegments == 0 || pieces.getSize() <= numSegments) return;
        if (queue.getSize() != pieces.getSize() - 1)
        {
            queue.clear();
            queue.reserve(pieces.getSize() - 1);
            auto it = pieces.begin();
            auto next = std::next(it);
            while (next != pieces.end())
            {
                queue.pushProvisionally(getMergeCost(*it, *next), *it);
                it = next;
                ++next;
            }
            queue.heapify();
        }

        while (pieces.getSize() != numSegments)
        {
            auto &&[cost, segment] = queue.pop();
            merge(segment, cost);
        }
    }

    /**
     * @brief Reduces the number of segments using a dynamic programming approach.
     *
     * @param numSegments Target number of segments.
     */
    void reduceDP(size_t numSegments)
    {
        queue.clear();
        if (numSegments == 0 || pieces.getSize() <= numSegments) return;

        // setup result table
        struct Entry
        {
            Scalar err = INFINITY;
            size_t size = 0;
        };
        std::unique_ptr<Entry[]> tvec(new Entry[pieces.getSize() * numSegments]);
        Entry *curRow = &tvec[0];

        // setup global regression (for col 1)
        Scalar *uniseg = &tempMemory[segSize];
        segInit(uniseg, 0, nullptr);

        // iterate over every row
        Scalar *curSegDiff = &tempMemory[2 * segSize];
        auto segit = pieces.begin();
        for (size_t segidx = 1; segit != pieces.end(); ++segidx, ++segit, curRow += numSegments)
        {
            // fill col 0
            segAdd(uniseg, uniseg, segGetStartPtr(*segit));
            segUpdateError(uniseg);
            curRow[0] = {uniseg[offErr], segidx};

            // fill other columns
            std::copy(uniseg, uniseg + segSize, curSegDiff);
            size_t diff = segidx;
            Entry *cmpRow = &tvec[0];
            for (auto cmpIt = pieces.begin(); --diff != 0; ++cmpIt, cmpRow += numSegments)
            {
                // compute additional error compared to row "cmp"
                segSub(curSegDiff, curSegDiff, segGetStartPtr(*cmpIt));
                segUpdateError(curSegDiff);
                auto err = curSegDiff[offErr];

                // check whether the error is smaller than currently used one
                for (size_t idx = 1; idx < numSegments; idx++)
                {
                    if (cmpRow[idx - 1].err + err < curRow[idx].err)
                    {
                        curRow[idx] = { cmpRow[idx - 1].err + err, diff };
                    }
                }
            }
        }

        curRow -= 1;
        auto mergeIt = List<Segment, Scalar>::Iterator::FromElement(pieces.back());
        for (size_t i = 0; i < numSegments; i++)
        {
            auto nextRow = curRow - (curRow->size * numSegments + 1);
            if (curRow->size != 0)
            {
                for (size_t i = 1; i < curRow->size; i++)
                {
                    auto prev = mergeIt--;
                    auto to = segGetStartPtr(*mergeIt);
                    segAdd(to, to, segGetStartPtr(*prev));
                    pieces.remove(prev);
                    mergeIt->sampleSize += prev->sampleSize;
                }
                segGetStartPtr(*mergeIt)[offErr] = curRow->err - nextRow->err;
                --mergeIt;
            }
            curRow = nextRow;
        }

        // delete queue so it gets rebuild in case od using greedy
        queue.clear();
    }

    /**
     * @brief Optimize the positions of the breakpoints, used after greedy reduce.
     *
     * @param data The same data that was placed to the placeSegements call.
     */
    void optimize(const Scalar *data) /// @TODO: Add parameter to determine opt-range
    {
        const auto optimizeBp = [=, this](Segment &s1, Segment &s2, size_t bpIdx)
        {
            const size_t start = bpIdx - s1.sampleSize / 4;
            const size_t end = bpIdx + s2.sampleSize / 4;
            const Scalar *row = data + start * (dimensions + variants);
            Scalar *s1p = segGetStartPtr(s1), *s2p = segGetStartPtr(s2);

            segSubPoints(s1p, bpIdx - start, row);
            segUpdateError(s1p);
            segAddPoints(s2p, bpIdx - start, row);
            segUpdateError(s2p);

            size_t idx = start;
            Scalar err1 = s1p[offErr], err2 = s2p[offErr], err = s1p[offErr] + s2p[offErr];
            for (size_t i = start; i < end; i++, row += dimensions + variants)
            {
                segAddPoints(s1p, 1, row);
                segUpdateError(s1p);
                segSubPoints(s2p, 1, row);
                segUpdateError(s2p);
                Scalar curErr1 = s1p[offErr];
                Scalar curErr2 = s2p[offErr];
                Scalar curErr = curErr1 + curErr2;
                if (curErr < err)
                {
                    err = curErr;
                    err1 = curErr1;
                    err2 = curErr2;
                    idx = i + 1;
                }
            }

            row -= (end - idx) * (dimensions + variants);
            segSubPoints(s1p, end - idx, row);
            segAddPoints(s2p, end - idx, row);
            s1p[offErr] = err1;
            s2p[offErr] = err2;
            s1.sampleSize += (idx - bpIdx);
            s2.sampleSize -= (idx - bpIdx);
        };

        struct OptEntry
        {
            size_t size, startPos;
            bool operator<(const OptEntry &other) const
            {
                return size > other.size;
            }
        };
        Heap<OptEntry, Segment> elements(queue.getSize() + 1);
        {
            auto start = pieces.begin();
            auto end = pieces.end();

            for (size_t startPos = start++->sampleSize; start != end; ++start)
            {
                elements.pushProvisionally({start->sampleSize, startPos}, *start);
                startPos += start->sampleSize;
            }
            elements.heapify();
        }

        while (!elements.isEmpty())
        {
            auto &&[entry, seg] = elements.pop();
            size_t startPos = entry.startPos;
            auto piece = List<Segment, Scalar>::Iterator::FromElement(seg);
            auto p = std::prev(piece);
            optimizeBp(*p, *piece, startPos);
        }

        // delete queue so it gets rebuild in case od using greedy
        queue.clear();
    }

    /**
     * @brief Get the rss of a specific segment.
     *
     * @param s A reference to a segment of this Mvsr instance.
     */
    Scalar getSegRss(const Segment &s) const
    {
        return segGetStartPtr(s)[offErr];
    }
    /**
     * @brief Get the model of a specific segment.
     *
     * @param s A reference to a segment of this Mvsr instance.
     * @param out A pointer to an output array of size $dimensions*variants$.
     */
    void getSegModel(const Segment &s, Scalar *out) const
    {
        segGetParams(segGetStartPtr(s), out);
    }
    /**
     * @brief Get the amount of source data samples belonging to a specific segment.
     *
     * @param s A reference to a segment of this Mvsr instance.
     */
    size_t getSegSize(const Segment &s) const
    {
        return s.sampleSize;
    }
    /**
     * @brief Get the amount of segments.
     */
    size_t getSegCount() const
    {
        return pieces.getSize();
    }
    /**
     * @brief Get the list of current segments.
     */
    const List<Segment, Scalar> &get() const
    {
        return pieces;
    }

    /**
     * @brief Get the amount of (input) dimensions.
     */
    size_t getDimensions() const
    {
        return dimensions;
    }
    /**
     * @brief Get the number of variants (output dimensions).
     */
    size_t getVariants() const
    {
        return variants;
    }

    //    Scalar getBsss(const Segment &s) const
    //    {
    //        const Scalar *base = &basemodel[0];
    //
    //        // calc regression model for segment
    //        const Scalar *seg = segGetStartPtr(s);
    //        Scalar bd[dimensions * variants];
    //        MatSolve(dimensions, variants, bd, seg + offX, seg + offY);
    //
    //        // subtract base model
    //        for (size_t i = 0; i < dimensions * variants; i++)
    //        {
    //            bd[i] -= base[i];
    //        }
    //
    //        // calculate summed distance
    //        return MatGsAAtPmulB(variants, dimensions, bd, seg + offX);
    //    }

private:
    void merge(Segment &seg, Scalar errIncr)
    {
        auto it = List<Segment, Scalar>::Iterator::FromElement(seg);
        auto nit = std::next(it);
        segMerge(*nit, *it, errIncr);
        pieces.remove(it);

        if (auto next = std::next(nit); next != pieces.end())
        {
            updateHeap(*nit, *next);
        }
        if (nit != pieces.begin())
        {
            updateHeap(*std::prev(nit), *nit);
        }
    }
    void updateHeap(Segment &seg, Segment &succ)
    {
        queue.update(seg, getMergeCost(seg, succ));
    }
    Scalar getMergeCost(const Segment &s1, const Segment &s2) const
    {
        return segGetMergedError(segGetStartPtr(s1), segGetStartPtr(s2)) -
               (segGetStartPtr(s1)[offErr] + segGetStartPtr(s2)[offErr]);
    }
    void segMerge(Segment &s1, const Segment &s2, Scalar errIncr)
    {
        Scalar *s1p = segGetStartPtr(s1);
        const Scalar *s2p = segGetStartPtr(s2);

        s1.sampleSize += s2.sampleSize;
        segAdd(s1p, s1p, s2p);
        s1p[offErr] += errIncr;
    }

    Scalar *segGetStartPtr(Segment &s)
    {
        return pieces.getExtraData(s);
    }
    const Scalar *segGetStartPtr(const Segment &s) const
    {
        return pieces.getExtraData(s);
    }

    void segInit(Scalar *start, size_t samples, const Scalar *data) const
    {
        for (size_t i = 0; i < dimensions * (dimensions + variants) + 2; i++)
        {
            start[i] = 0;
        }
        segAddPoints(start, samples, data);
        if (samples > dimensions)
        {
            segUpdateError(start);
        }
    }
    void segAdd(Scalar *res, const Scalar *s1, const Scalar *s2) const
    {
        for (size_t i = 0; i < dimensions * (dimensions + variants) + 2; i++)
        {
            res[i] = s1[i] + s2[i];
        }
    }
    void segSub(Scalar *res, const Scalar *s1, const Scalar *s2) const
    {
        for (size_t i = 0; i < dimensions * (dimensions + variants) + 2; i++)
        {
            res[i] = s1[i] - s2[i];
        }
    }
    void segAddPoints(Scalar *start, size_t samples, const Scalar *data) const
    {
        Scalar *xmat = start + offX;
        Scalar *ymat = start + offY;
        Scalar y2 = Scalar(0);
        for (size_t s = 0; s < samples; s++, data += dimensions + variants)
        {
            for (size_t y = 0; y < dimensions; y++)
            {
                for (size_t x = 0; x < dimensions; x++)
                {
                    xmat[y * dimensions + x] += data[x] * data[y];
                }
                for (size_t v = 0; v < variants; v++)
                {
                    ymat[y * variants + v] += data[y] * data[dimensions + v];
                }
            }
            for (size_t v = dimensions; v < dimensions + variants; v++)
            {
                y2 += data[v] * data[v];
            }
        }
        start[offY2] += y2;
    }
    void segSubPoints(Scalar *start, size_t samples, const Scalar *data) const
    {
        Scalar *xmat = start + offX;
        Scalar *ymat = start + offY;
        Scalar y2 = Scalar(0);
        for (size_t s = 0; s < samples; s++, data += dimensions + variants)
        {
            for (size_t y = 0; y < dimensions; y++)
            {
                for (size_t x = 0; x < dimensions; x++)
                {
                    xmat[y * dimensions + x] -= data[x] * data[y];
                }
                for (size_t v = 0; v < variants; v++)
                {
                    ymat[y * variants + v] -= data[y] * data[dimensions + v];
                }
            }
            for (size_t v = dimensions; v < dimensions + variants; v++)
            {
                y2 += data[v] * data[v];
            }
        }
        start[offY2] -= y2;
    }

    void segGetParams(const Scalar *sptr, Scalar *out) const
    {
        const Scalar *xm = sptr + offX;
        const Scalar *ym = sptr + offY;
        MatSolve(dimensions, variants, &tempMemory[0], xm, ym);
        std::copy(&tempMemory[0], &tempMemory[dimensions*variants], out);
    }
    Scalar segCalcError(const Scalar *seg) const
    {
        Scalar *params = &tempMemory[0];
        const Scalar *xm = &seg[offX];
        const Scalar *ym = &seg[offY];
        MatSolve(dimensions, variants, params, xm, ym);

        Scalar res = Scalar(0);
        for (size_t i = 0; i < dimensions * variants; i++)
        {
            res += params[i] * ym[i];
        }
        res *= Scalar(-2);

        res += MatGsAAtPmulB(variants, dimensions, params, xm);
        res += seg[offY2];

        return res;
    }
    void segUpdateError(Scalar *seg) const
    {
        seg[offErr] = segCalcError(seg);
    }
    Scalar segGetMergedError(const Scalar *s1, const Scalar *s2) const
    {
        Scalar *merged = &tempMemory[segSize];
        segAdd(merged, s1, s2);

        return segCalcError(merged);
    }

    const size_t dimensions;
    const size_t variants;

    constexpr static size_t offErr = 0;
    constexpr static size_t offY2 = 1;
    constexpr static size_t offX = 2;
    const size_t offY;
    const size_t segSize;
    
    Heap<Scalar, Segment> queue;                // Priority queue with the merge costs
    List<Segment, Scalar> pieces;               // Double linked list, containing the segments
    // Scalar rss = Scalar(0);                    // Current summed squared error
    // std::shared_ptr<Scalar[]> basemodel;       // Parameter matrix for regression with k=1
    const std::unique_ptr<Scalar[]> tempMemory; // needed to store some matrices for calculations
};

#endif // guard
