// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#include "PMFTXYZ.h"
#include "Histogram.h"
#include "ManagedArray.h"
#include "NeighborBond.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "PMFT.h"
#include "VectorMath.h"
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>

/*! \file PMFTXYZ.cc
    \brief Routines for computing 3D potential of mean force in XYZ coordinates
*/

namespace freud { namespace pmft {

PMFTXYZ::PMFTXYZ(float x_max, float y_max, float z_max, unsigned int n_x, unsigned int n_y, unsigned int n_z)
    : PMFT(), m_num_equiv_orientations(0xffffffff)
{
    if (n_x < 1)
    {
        throw std::invalid_argument("PMFTXYZ requires at least 1 bin in X.");
    }
    if (n_y < 1)
    {
        throw std::invalid_argument("PMFTXYZ requires at least 1 bin in Y.");
    }
    if (n_z < 1)
    {
        throw std::invalid_argument("PMFTXYZ requires at least 1 bin in Z.");
    }
    if (x_max < 0)
    {
        throw std::invalid_argument("PMFTXYZ requires that x_max must be positive.");
    }
    if (y_max < 0)
    {
        throw std::invalid_argument("PMFTXYZ requires that y_max must be positive.");
    }
    if (z_max < 0)
    {
        throw std::invalid_argument("PMFTXYZ requires that z_max must be positive.");
    }

    // Compute Jacobian
    const float dx = float(2.0) * x_max / float(n_x);
    const float dy = float(2.0) * y_max / float(n_y);
    const float dz = float(2.0) * z_max / float(n_z);

    // Note: To properly normalize, we must consider the 3 degrees of freedom
    // that are implicitly integrated over by this calculation. In three
    // dimensions, there are 6 total degrees of freedom; we are only accounting
    // for the relative positions. The orientational degrees of freedom of the
    // second particle constitute the other three. The total volume in our 6D
    // coordinate space accounted for by these orientational degrees of freedom
    // is 8*pi^2. To see this, consider an integral over the Euler angles as
    // shown here
    // https://en.wikipedia.org/wiki/3D_rotation_group#Spherical_harmonics or
    // discussed more in depth in Representations of the Rotation and Lorentz
    // Groups and Their Applications by Gelfand, Minlos, and Shapiro.
    // However, this factor is implicitly canceled out since we also do not
    // include it in the number density computed for the system, see
    // PMFT::reduce for more information.
    m_jacobian = dx * dy * dz;

    // Create the PCF array.
    m_pcf_array = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {n_x, n_y, n_z});

    // Construct the Histogram object that will be used to keep track of counts
    // of bond distances found.
    const auto axes = util::Axes {std::make_shared<util::RegularAxis>(n_x, -x_max, x_max),
                                  std::make_shared<util::RegularAxis>(n_y, -y_max, y_max),
                                  std::make_shared<util::RegularAxis>(n_z, -z_max, z_max)};
    m_histogram = BondHistogram(axes);
    m_local_histograms = BondHistogram::ThreadLocalHistogram(m_histogram);
}

// Almost identical to the parent method, except that the normalization factor
// in this class also includes the number of equivalent orientations.
void PMFTXYZ::reduce()
{
    float const inv_num_dens = m_box.getVolume() / (float) m_n_query_points;
    float const norm_factor
        = (float) 1.0 / ((float) m_frame_counter * (float) m_n_points * (float) m_num_equiv_orientations);
    float prefactor = inv_num_dens * norm_factor;

    float jacobian_factor = (float) 1.0 / m_jacobian;
    m_histogram.reduceOverThreadsPerBin(m_local_histograms, [this, &prefactor, &jacobian_factor](size_t i) {
        (*m_pcf_array)[i] = static_cast<float>(m_histogram[i]) * prefactor * jacobian_factor;
    });
}

void PMFTXYZ::reset()
{
    PMFT::reset();
    m_num_equiv_orientations = 0xffffffff;
}

void PMFTXYZ::accumulate(const std::shared_ptr<locality::NeighborQuery>& neighbor_query,
                         const quat<float>* query_orientations, const vec3<float>* query_points,
                         unsigned int n_query_points, const quat<float>* equiv_orientations,
                         unsigned int num_equiv_orientations, std::shared_ptr<locality::NeighborList> nlist,
                         const freud::locality::QueryArgs& qargs)
{
    // Set the number of equivalent orientations the first time we compute
    // (after a reset), then error on subsequent calls if it changes.
    if (m_num_equiv_orientations == 0xffffffff)
    {
        m_num_equiv_orientations = num_equiv_orientations;
    }
    else if (m_num_equiv_orientations != num_equiv_orientations)
    {
        throw std::runtime_error(
            "The number of equivalent orientations must be constant while accumulating data into PMFTXYZ.");
    }
    neighbor_query->getBox().enforce3D();

    // accumulate thread-local arrays
    accumulateGeneral(neighbor_query, query_points, n_query_points, std::move(nlist), qargs,
                      [&](const freud::locality::NeighborBond& neighbor_bond) {
                          // create the reference point quaternion
                          const quat<float> query_orientation(
                              query_orientations[neighbor_bond.getQueryPointIdx()]);
                          // make sure that the particles are wrapped into the box
                          const vec3<float>& delta(neighbor_bond.getVector());

                          for (unsigned int k = 0; k < num_equiv_orientations; k++)
                          {
                              // create point vector
                              vec3<float> v(delta);
                              // rotate the vector
                              v = rotate(conj(query_orientation), v);
                              v = rotate(equiv_orientations[k], v);

                              m_local_histograms(v.x, v.y, v.z);
                          }
                      });
}

}; }; // end namespace freud::pmft
