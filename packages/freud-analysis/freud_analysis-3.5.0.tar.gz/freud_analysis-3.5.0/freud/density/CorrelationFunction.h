// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#ifndef CORRELATION_FUNCTION_H
#define CORRELATION_FUNCTION_H

#include <complex>
#include <memory>

#include "BondHistogramCompute.h"
#include "Histogram.h"
#include "ManagedArray.h"
#include "NeighborList.h"
#include "NeighborQuery.h"
#include "VectorMath.h"

/*! \file CorrelationFunction.h
    \brief Generic pairwise correlation functions.
*/

namespace freud { namespace density {

//! Computes the pairwise correlation function <p*q>(r) between two sets of points with associated values p
//! and q.
/*! Two sets of points and two sets of values associated with those
    points are given. Computing the correlation function results in an
    array of the expected (average) product of all values at a given
    radial distance.

    The values of r at which to compute the correlation function are
    controlled by the r_max and dr parameters to the constructor. r_max
    determines the maximum r at which to compute the correlation
    function and dr is the step size for each bin.

    <b>2D:</b><br>
    CorrelationFunction properly handles 2D boxes. As with everything
    else in freud, 2D points must be passed in as 3 component vectors
    x,y,0. Failing to set 0 in the third component will lead to
    undefined behavior.

    <b>Self-correlation:</b><br>
    It is often the case that we wish to compute the correlation
    function of a set of points with itself. If given the same arrays
    for both points and ref_points, we omit accumulating the
    self-correlation value in the first bin.

*/
class CorrelationFunction : public locality::BondHistogramCompute
{
public:
    //! Constructor
    CorrelationFunction(unsigned int bins, float r_max);

    //! Destructor
    ~CorrelationFunction() override = default;

    //! Reset the PCF array to all zeros
    void reset() override;

    //! accumulate the correlation function
    void accumulate(const std::shared_ptr<freud::locality::NeighborQuery>& neighbor_query,
                    const std::complex<double>* values, const vec3<float>* query_points,
                    const std::complex<double>* query_values, unsigned int n_query_points,
                    const std::shared_ptr<freud::locality::NeighborList>& nlist,
                    const freud::locality::QueryArgs& qargs);

    //! \internal
    //! helper function to reduce the thread specific arrays into one array
    void reduce() override;

    //! Get a reference to the last computed correlation function.
    std::shared_ptr<util::ManagedArray<std::complex<double>>> getCorrelation()
    {
        return reduceAndReturn(m_correlation_function.getBinCounts());
    }

private:
    // Typedef thread local histogram type for use in code.
    using CFThreadHistogram = typename util::Histogram<std::complex<double>>::ThreadLocalHistogram;

    util::Histogram<std::complex<double>> m_correlation_function; //!< The correlation function
    CFThreadHistogram m_local_correlation_function; //!< Thread local copy of the correlation function
};

}; }; // end namespace freud::density

#endif // CORRELATION_FUNCTION_H
