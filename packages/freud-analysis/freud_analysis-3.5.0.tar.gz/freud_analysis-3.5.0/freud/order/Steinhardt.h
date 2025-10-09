// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#ifndef STEINHARDT_H
#define STEINHARDT_H

#include <algorithm>
#include <complex>
#include <cstddef>
#include <memory>
#include <vector>

#include "ManagedArray.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "ThreadStorage.h"
#include "fsph/src/spherical_harmonics.hpp"

/*! \file Steinhardt.h
    \brief Computes variants of Steinhardt order parameters.
*/

namespace freud { namespace order {

using YlmsType = std::vector<std::vector<std::complex<float>>>;

//! Compute the Steinhardt local rotationally invariant ql or wl order parameter for a set of points
/*!
 * Implements the rotationally invariant ql or wl order parameter described
 * by Steinhardt. For a particle i, we calculate the average q_l by summing
 * the spherical harmonics between particle i and its neighbors j in a local
 * region:
 * \f$ \overline{q}_{lm}(i) = \frac{1}{N_b} \sum \limits_{j=1}^{N_b}
 * Y_{lm}(\theta(\vec{r}_{ij}),\phi(\vec{r}_{ij})) \f$
 *
 * This is then combined in a rotationally invariant fashion to remove local
 * orientational order as follows:
 * \f$ q_l(i)=\sqrt{\frac{4\pi}{2l+1} \sum \limits_{m=-l}^{l} |\overline{q}_{lm}|^2 }  \f$
 *
 * If the average flag is set, the order parameters averages over the second neighbor shell.
 * For a particle i, we calculate the average q_l by summing the spherical
 * harmonics between particle i and its neighbors j and the neighbors k of
 * neighbor j in a local region.
 *
 * If the norm flag is set, the ql value is normalized by the average qlm value
 * for the system.
 *
 * If the flag wl is set, the third-order invariant wl order parameter will
 * be calculated. wl can aid in distinguishing between FCC, HCP, and BCC.
 *
 * If the flag wl_normalize is set, the third-order invariant wl order parameter
 * will be normalized.
 *
 * For more details see:
 * - PJ Steinhardt (1983) (DOI: 10.1103/PhysRevB.28.784)
 * - Wolfgang Lechner (2008) (DOI: 10.1063/Journal of Chemical Physics 129.114707)
 */

class Steinhardt
{
public:
    //! Steinhardt Class Constructor
    /*! Constructor for Steinhardt analysis class.
     *  \param ls Spherical harmonic numbers l. Must be non-negative integers.
     */
    explicit Steinhardt(const std::vector<unsigned int>& ls, bool average = false, bool wl = false,
                        bool weighted = false, bool wl_normalize = false)
        : m_ls(ls), m_num_ms(m_ls.size()), m_average(average), m_wl(wl), m_weighted(weighted),
          m_wl_normalize(wl_normalize), m_qlm_local(m_ls.size()), m_qlmi(ls.size()), m_qlm(ls.size()),
          m_qlmiAve(ls.size()), m_qlmAve(ls.size())

    {
        std::transform(m_ls.cbegin(), m_ls.cend(), m_num_ms.begin(), [](const auto& l) { return 2 * l + 1; });
        std::transform(m_ls.cbegin(), m_ls.cend(), m_qlm_local.begin(),
                       [](const auto& l) { return util::ThreadStorage<std::complex<float>>(2 * l + 1); });
    }

    //! Steinhardt Class Constructor
    /*! Constructor for Steinhardt analysis class.
     *  \param l Spherical harmonic number l. Must be non-negative integers.
     */
    explicit Steinhardt(const unsigned int l, bool average = false, bool wl = false, bool weighted = false,
                        bool wl_normalize = false)
        : Steinhardt(std::vector<unsigned int> {l}, average, wl, weighted, wl_normalize)
    {}

    //! Empty destructor
    ~Steinhardt() = default;

    //! Get the number of particles used in the last compute
    unsigned int getNP() const
    {
        return m_Np;
    }

    //! Get the last calculated order parameter for each l
    const std::shared_ptr<util::ManagedArray<float>>& getParticleOrder() const
    {
        if (m_wl)
        {
            return m_wli;
        }
        return getQl();
    }

    //! Get the last calculated ql for each l
    const std::shared_ptr<util::ManagedArray<float>>& getQl() const
    {
        if (m_average)
        {
            return m_qliAve;
        }
        return m_qli;
    }

    //! Get the last calculated qlm for each particle and l
    const std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>>& getQlm() const
    {
        return m_qlmi;
    }

    //! Get system-normalized order for each l
    std::vector<float> getOrder() const
    {
        return m_norm;
    }

    //!< Whether to take a second shell average
    bool isAverage() const
    {
        return m_average;
    }

    //!< Whether to use the third-order invariant wl
    bool isWl() const
    {
        return m_wl;
    }

    //!< Whether to use neighbor weights in computing qlmi
    bool isWeighted() const
    {
        return m_weighted;
    }

    //!< Whether to normalize the third-order invariant wl
    bool isWlNormalized() const
    {
        return m_wl_normalize;
    }

    //! Compute the order parameter
    void compute(const std::shared_ptr<freud::locality::NeighborList>& nlist,
                 const std::shared_ptr<freud::locality::NeighborQuery>& points,
                 const freud::locality::QueryArgs& qargs);

    std::vector<unsigned int> getL() const
    {
        return m_ls;
    }

private:
    //! \internal
    //! Spherical harmonics calculation for Ylm filling a
    //  std::vector<std::vector<std::complex<float> > > with values for m = 0, 1, ..., l, -1, ..., -l
    //  for all l in m_ls
    void computeYlm(fsph::PointSPHEvaluator<float>& sph_eval, const float theta, const float phi,
                    YlmsType& Ylms) const;

    template<typename T> std::shared_ptr<T> makeArray(size_t size);

    //! Reallocates only the necessary arrays when the number of particles changes
    // unsigned int Np number of particles
    void reallocateArrays(unsigned int Np);

    //! Calculates qlms and the ql order parameter before any further modifications
    void baseCompute(const std::shared_ptr<freud::locality::NeighborList>& nlist,
                     const std::shared_ptr<freud::locality::NeighborQuery>& points,
                     const freud::locality::QueryArgs& qargs);

    //! Calculates the neighbor average ql order parameter
    void computeAve(const std::shared_ptr<freud::locality::NeighborList>& nlist,
                    const std::shared_ptr<freud::locality::NeighborQuery>& points,
                    const freud::locality::QueryArgs& qargs);

    //! Compute the system-wide order by averaging over particles, then
    //  reducing over the m values to produce a single scalar.
    std::vector<float> normalizeSystem();

    //! Sum over Wigner 3j coefficients to compute third-order invariants
    //  wl from second-order invariants ql
    void aggregatewl(std::shared_ptr<util::ManagedArray<float>>& target,
                     const std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>>& source,
                     const std::shared_ptr<util::ManagedArray<float>>& normalization_source) const;

    // Member variables used for compute
    unsigned int m_Np {0};              //!< Last number of points computed
    std::vector<unsigned int> m_ls;     //!< Spherical harmonic l values.
    std::vector<unsigned int> m_num_ms; //!< The number of magnetic quantum numbers for each l (2*l+1).

    // Flags
    bool m_average;      //!< Whether to take a second shell average (default false)
    bool m_wl;           //!< Whether to use the third-order invariant wl (default false)
    bool m_weighted;     //!< Whether to use neighbor weights in computing qlmi (default false)
    bool m_wl_normalize; //!< Whether to normalize the third-order invariant wl (default false)

    std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>> m_qlmi; //!< qlm for each particle i
    std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>>
        m_qlm; //!< Normalized qlm(Ave) for the whole system
    std::vector<util::ThreadStorage<std::complex<float>>>
        m_qlm_local; //!< Thread-specific m_qlm(Ave) for each l
    std::shared_ptr<util::ManagedArray<float>>
        m_qli; //!< ql locally invariant order parameter for each particle i
    std::shared_ptr<util::ManagedArray<float>>
        m_qliAve; //!< Averaged ql with 2nd neighbor shell for each particle i
    std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>>
        m_qlmiAve; //!< Averaged qlm with 2nd neighbor shell for each particle i
    std::vector<std::shared_ptr<util::ManagedArray<std::complex<float>>>>
        m_qlmAve;                  //!< Normalized qlmiAve for the whole system
    std::vector<float> m_norm {0}; //!< System normalized order parameter
    std::shared_ptr<util::ManagedArray<float>>
        m_wli; //!< wl order parameter for each particle i, also used for wl averaged data
};

}; };  // end namespace freud::order
#endif // STEINHARDT_H
