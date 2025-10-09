// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#include <cmath>
#include <cstddef>
#include <memory>
#include <vector>

#include "ManagedArray.h"
#include "Nematic.h"
#include "VectorMath.h"
#include "diagonalize.h"
#include "utils.h"

/*! \file Nematic.h
    \brief Compute the nematic order parameter for each particle
*/

namespace freud { namespace order {

float Nematic::getNematicOrderParameter() const
{
    return m_nematic_order_parameter;
}

std::shared_ptr<const util::ManagedArray<float>> Nematic::getParticleTensor() const
{
    return m_particle_tensor;
}

std::shared_ptr<const util::ManagedArray<float>> Nematic::getNematicTensor() const
{
    return m_nematic_tensor;
}

unsigned int Nematic::getNumParticles() const
{
    return m_n;
}

vec3<float> Nematic::getNematicDirector() const
{
    return m_nematic_director;
}

void Nematic::compute(const vec3<float>* orientations, unsigned int n)
{
    m_n = n;
    m_particle_tensor = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {m_n, 3, 3});
    m_nematic_tensor_local->reset();

    // calculate per-particle tensor
    util::forLoopWrapper(0, n, [&](size_t begin, size_t end) {
        for (size_t i = begin; i < end; ++i)
        {
            // get the orientation of the particle and normalize it
            auto u_i = orientations[i];
            u_i = u_i / std::sqrt(dot(u_i, u_i));

            util::ManagedArray<float> Q_ab({3, 3});

            Q_ab(0, 0) = 1.5F * u_i.x * u_i.x - 0.5F;
            Q_ab(0, 1) = 1.5F * u_i.x * u_i.y;
            Q_ab(0, 2) = 1.5F * u_i.x * u_i.z;
            Q_ab(1, 0) = 1.5F * u_i.y * u_i.x;
            Q_ab(1, 1) = 1.5F * u_i.y * u_i.y - 0.5F;
            Q_ab(1, 2) = 1.5F * u_i.y * u_i.z;
            Q_ab(2, 0) = 1.5F * u_i.z * u_i.x;
            Q_ab(2, 1) = 1.5F * u_i.z * u_i.y;
            Q_ab(2, 2) = 1.5F * u_i.z * u_i.z - 0.5F;

            // Set the values. The nematic tensor is reduced later.
            for (unsigned int j = 0; j < 3; j++)
            {
                for (unsigned int k = 0; k < 3; k++)
                {
                    (*m_particle_tensor)(i, j, k) += Q_ab(j, k);
                    m_nematic_tensor_local->local()(j, k) += Q_ab(j, k);
                }
            }
        }
    });

    // Now calculate the sum of Q_ab's
    m_nematic_tensor = std::make_shared<util::ManagedArray<float>>(std::vector<size_t> {3, 3});
    m_nematic_tensor_local->reduceInto(*m_nematic_tensor);

    // Normalize by the number of particles
    for (unsigned int i = 0; i < m_nematic_tensor->size(); ++i)
    {
        (*m_nematic_tensor)[i] /= static_cast<float>(m_n);
    }

    // the order parameter is the eigenvector belonging to the largest eigenvalue
    util::ManagedArray<float> eval = util::ManagedArray<float>(3);
    util::ManagedArray<float> evec = util::ManagedArray<float>({3, 3});

    freud::util::diagonalize33SymmetricMatrix(*m_nematic_tensor, eval, evec);
    m_nematic_director = vec3<float>(evec(2, 0), evec(2, 1), evec(2, 2));
    m_nematic_order_parameter = eval[2];
}

}; }; // end namespace freud::order
