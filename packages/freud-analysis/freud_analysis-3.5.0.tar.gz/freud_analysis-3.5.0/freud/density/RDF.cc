// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#include <cstddef>
#include <math.h> // NOLINT(modernize-deprecated-headers): Use std::numbers when c++20 is default.
#include <memory>
#include <stdexcept>
#include <vector>

#include "BondHistogramCompute.h"
#include "Histogram.h"
#include "ManagedArray.h"
#include "NeighborBond.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "RDF.h"
#include "VectorMath.h"

/*! \file RDF.cc
    \brief Routines for computing radial density functions.
*/

namespace freud { namespace density {

RDF::RDF(unsigned int bins, float r_max, float r_min) : BondHistogramCompute()
{
    if (bins == 0)
    {
        throw std::invalid_argument("RDF requires a nonzero number of bins.");
    }
    if (r_max <= 0)
    {
        throw std::invalid_argument("RDF requires r_max to be positive.");
    }
    if (r_min < 0)
    {
        throw std::invalid_argument("RDF requires r_min to be non-negative.");
    }
    if (r_max <= r_min)
    {
        throw std::invalid_argument("RDF requires that r_max must be greater than r_min.");
    }

    // Construct the Histogram object that will be used to keep track of counts of bond distances found.
    const auto axes = util::Axes {std::make_shared<util::RegularAxis>(bins, r_min, r_max)};
    m_histogram = BondHistogram(axes);
    m_local_histograms = BondHistogram::ThreadLocalHistogram(m_histogram);
    m_pcf = std::make_shared<util::ManagedArray<float>>(m_histogram.shape());
    m_N_r = std::make_shared<util::ManagedArray<float>>(m_histogram.shape());

    // Precompute the cell volumes to speed up later calculations.
    m_vol_array2D = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {bins, bins});
    m_vol_array3D = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {bins, bins, bins});
    const float volume_prefactor = (float(4.0) / float(3.0)) * M_PI;
    std::vector<float> bin_boundaries = getBinEdges()[0];

    for (unsigned int i = 0; i < bins; i++)
    {
        const float r = bin_boundaries[i];
        const float nextr = bin_boundaries[i + 1];
        (*m_vol_array2D)[i] = M_PI * (nextr * nextr - r * r);
        (*m_vol_array3D)[i] = volume_prefactor * (nextr * nextr * nextr - r * r * r);
    }
}

void RDF::reset()
{
    BondHistogramCompute::reset();
    m_pcf = std::make_shared<util::ManagedArray<float>>(m_pcf->shape());
    m_N_r = std::make_shared<util::ManagedArray<float>>(m_N_r->shape());
}

void RDF::reduce()
{
    // Define prefactors with appropriate types to simplify and speed later code.
    auto const nqp = static_cast<float>(m_n_query_points);
    float number_density = nqp / m_box.getVolume();
    if (mode == NormalizationMode::finite_size)
    {
        number_density *= static_cast<float>(m_n_query_points - 1) / static_cast<float>(m_n_query_points);
    }
    auto np = static_cast<float>(m_n_points);
    auto nf = static_cast<float>(m_frame_counter);
    float prefactor = float(1.0) / (np * number_density * nf);

    std::shared_ptr<util::ManagedArray<float>> vol_array = m_box.is2D() ? m_vol_array2D : m_vol_array3D;
    m_histogram.reduceOverThreadsPerBin(m_local_histograms, [this, &prefactor, &vol_array](size_t i) {
        (*m_pcf)[i] = float(m_histogram[i]) * prefactor / (*vol_array)[i];
    });

    // The accumulation of the cumulative density must be performed in
    // sequence, so it is done after the reduction.
    prefactor = float(1.0) / (nqp * static_cast<float>(m_frame_counter));
    (*m_N_r)[0] = float(m_histogram[0]) * prefactor;
    for (unsigned int i = 1; i < getAxisSizes()[0]; i++)
    {
        (*m_N_r)[i] = (*m_N_r)[i - 1] + float(m_histogram[i]) * prefactor;
    }
}

void RDF::accumulate(const std::shared_ptr<freud::locality::NeighborQuery>& neighbor_query,
                     const vec3<float>* query_points, unsigned int n_query_points,
                     const std::shared_ptr<freud::locality::NeighborList>& nlist,
                     const freud::locality::QueryArgs& qargs)
{
    accumulateGeneral(neighbor_query, query_points, n_query_points, nlist, qargs,
                      [&](const freud::locality::NeighborBond& neighbor_bond) {
                          m_local_histograms(neighbor_bond.getDistance());
                      });
}

}; }; // end namespace freud::density
