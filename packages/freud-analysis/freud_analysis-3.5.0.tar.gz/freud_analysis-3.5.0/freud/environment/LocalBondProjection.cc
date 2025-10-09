// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#include <cstddef>
#include <memory>
#include <vector>

#include "LocalBondProjection.h"
#include "ManagedArray.h"
#include "NeighborComputeFunctional.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "VectorMath.h"
#include "utils.h"

/*! \file LocalBondProjection.h
    \brief Compute the projection of nearest neighbor bonds for each particle onto some
    set of reference vectors, defined in the particles' local reference frame.
*/

namespace freud { namespace environment {

// The set of all equivalent quaternions equiv_qs is the set that takes the particle as it
// is defined to some global reference orientation. Thus, to be safe, we must include
// a rotation by qconst as defined below when doing the calculation.
// IMPT: equiv_qs does NOT have to include both q and -q, for all included quaternions.
// Rather, equiv_qs SHOULD contain the identity, and have the same length as the order of
// the chiral symmetry group of the particle shape.
// q and -q effect the same rotation on vectors, and here we just use equiv_quats to
// find all symmetrically equivalent vectors to proj_vec.
float computeMaxProjection(const vec3<float>& proj_vec, const vec3<float>& local_bond,
                           const quat<float>* equiv_qs, unsigned int n_equiv_qs)
{
    const quat<float> qconst = equiv_qs[0];

    // start with the reference vector before it has been rotated by equivalent quaternions
    float max_proj = dot(proj_vec, local_bond);

    // loop through all equivalent rotations and see if they have a larger projection onto local_bond
    for (unsigned int i = 0; i < n_equiv_qs; i++)
    {
        const quat<float> qe = equiv_qs[i];
        // here we undo a rotation represented by one of the equivalent orientations
        const quat<float> qtest = conj(qconst) * qe;
        const vec3<float> equiv_proj_vec = rotate(qtest, proj_vec);

        const float proj_test = dot(equiv_proj_vec, local_bond);

        if (proj_test > max_proj)
        {
            max_proj = proj_test;
        }
    }

    return max_proj;
}

void LocalBondProjection::compute(const std::shared_ptr<locality::NeighborQuery>& nq,
                                  const quat<float>* orientations, const vec3<float>* query_points,
                                  unsigned int n_query_points, const vec3<float>* proj_vecs,
                                  unsigned int n_proj, const quat<float>* equiv_orientations,
                                  unsigned int n_equiv_orientations,
                                  const std::shared_ptr<freud::locality::NeighborList>& nlist,
                                  const locality::QueryArgs& qargs)
{
    // This function requires a NeighborList object, so we always make one and store it locally.
    m_nlist = locality::makeDefaultNlist(nq, nlist, query_points, n_query_points, qargs);

    // Get the maximum total number of bonds in the neighbor list
    const unsigned int tot_num_neigh = m_nlist->getNumBonds();
    const auto& neighbors = m_nlist->getNeighbors();

    m_local_bond_proj
        = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {tot_num_neigh, n_proj});
    m_local_bond_proj_norm
        = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {tot_num_neigh, n_proj});

    // compute the order parameter
    util::forLoopWrapper(0, n_query_points, [&](size_t begin, size_t end) {
        size_t bond(m_nlist->find_first_index(begin));
        for (size_t i = begin; i < end; ++i)
        {
            for (; bond < tot_num_neigh && (*neighbors)(bond, 0) == i; ++bond)
            {
                const size_t j((*neighbors)(bond, 1));

                // compute bond vector between the two particles
                vec3<float> local_bond((*m_nlist->getVectors())(bond));

                // rotate bond vector into the local frame of particle p
                local_bond = rotate(conj(orientations[j]), local_bond);
                // store the length of this local bond
                const float local_bond_len = (*m_nlist->getDistances())(bond);

                for (unsigned int k = 0; k < n_proj; k++)
                {
                    const vec3<float> proj_vec = proj_vecs[k];
                    const float max_proj = computeMaxProjection(proj_vec, local_bond, equiv_orientations,
                                                                n_equiv_orientations);
                    (*m_local_bond_proj)(bond, k) = max_proj;
                    (*m_local_bond_proj_norm)(bond, k) = max_proj / local_bond_len;
                }
            }
        }
    });
}

}; }; // end namespace freud::environment
