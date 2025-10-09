cimport cython
from cython.operator cimport address
from libc.math cimport cos, isnan, log, sin

import numpy as np

cimport numpy as np

DEF NUM_SAMPLE = 21
DEF DEBUG_OUTPUT = 0
DEF PRECISION = 1e-8


cdef extern from "sici.h":

    void sici(double, double*, double*) nogil



@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)   # turn off negative index wrapping for entire function
@cython.cdivision(True)
cdef double trapez(double *x, double *y, size_t n) nogil:
    cdef double integral = 0.0
    cdef size_t i
    for i in range(0, n - 1):
        integral += (x[i + 1] - x[i]) * (y[i] + y[i + 1])
    return integral / 2.0


cdef struct context:
    int nsun, na, hp
    double *f_ptr
    double *nu_range_ptr
    double *log_nu
    double *c_ptr
    double *k_ptr
    double *integrand
    double *m_msun_ptr
    double *rv_mpc_ptr
    double *bias_ptr


@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.initializedcheck(False)
cpdef _integral_halo(np.ndarray[double, ndim=1] k,
                     np.ndarray[double, ndim=1] m_msun,
                     np.ndarray[double, ndim=2] nu_range,
                     np.ndarray[double, ndim=2] bias,
                     np.ndarray[double, ndim=2] rv_mpc,
                     np.ndarray[double, ndim=2] c,
                     np.ndarray[double, ndim=1] a,
                     np.ndarray[double, ndim=2] f,
                     int halo_profile,
                     int adaptive
                     ):

    cdef np.ndarray[double, ndim=1, mode = 'c'] k_buff = np.ascontiguousarray(k)
    cdef double * k_ptr = <double *> k_buff.data

    cdef size_t hp = halo_profile
    cdef size_t nsun = m_msun.shape[0]
    cdef size_t na = a.shape[0]
    cdef size_t nk = k.shape[0]
    assert nu_range.shape[0] == na, nu_range.shape[0]
    assert nu_range.shape[1] == nsun, nu_range.shape[1]
    assert bias.shape[0] == na, bias.shape[0]
    assert bias.shape[1] == nsun, bias.shape[1]
    assert rv_mpc.shape[0] == na, rv_mpc.shape[0]
    assert rv_mpc.shape[1] == nsun, rv_mpc.shape[1]
    assert c.shape[0] == na, c.shape[0]
    assert c.shape[1] == nsun, c.shape[1]
    assert f.shape[0] == na, f.shape[0]
    assert f.shape[1] == nsun, f.shape[1]

    cdef np.ndarray[double, ndim=1] integrand_a
    cdef np.ndarray[double, ndim=2] log_nu_a
    cdef np.ndarray[double, ndim=1] log_nu_ai
    cdef np.ndarray[double, ndim=2] result

    integrand_a = np.zeros((nsun,), dtype=np.float64)
    log_nu_a = np.zeros((na, nsun,), dtype=np.float64)
    log_nu_ai = np.zeros((nsun,), dtype=np.float64)
    result = np.zeros((nk, na,), dtype=np.float64)

    cdef np.ndarray[double, ndim=2, mode = 'c'] rv_mpc_buff = np.ascontiguousarray(rv_mpc)
    cdef double * rv_mpc_ptr = <double *> rv_mpc_buff.data

    cdef np.ndarray[double, ndim=1, mode = 'c'] m_msun_buff = np.ascontiguousarray(m_msun)
    cdef double * m_msun_ptr = <double *> m_msun_buff.data

    cdef np.ndarray[double, ndim=2, mode = 'c'] bias_buff = np.ascontiguousarray(bias)
    cdef double * bias_ptr = <double *> bias_buff.data

    cdef np.ndarray[double, ndim=1, mode = 'c'] integrand_buff = np.ascontiguousarray(integrand_a)
    cdef double * integrand_ptr = <double *> integrand_buff.data

    cdef np.ndarray[double, ndim=2, mode = 'c'] c_buff = np.ascontiguousarray(c)
    cdef double * c_ptr = <double *> c_buff.data

    cdef np.ndarray[double, ndim=2, mode = 'c'] f_buff = np.ascontiguousarray(f)
    cdef double * f_ptr = <double *> f_buff.data

    cdef np.ndarray[double, ndim=2, mode = 'c'] nu_range_buff = np.ascontiguousarray(nu_range)
    cdef double * nu_range_ptr = <double *> nu_range_buff.data

    cdef np.ndarray[double, ndim=2, mode = 'c'] log_nu_buff = np.ascontiguousarray(log_nu_a)
    cdef double * log_nu_ptr = <double *> log_nu_buff.data

    cdef np.ndarray[double, ndim=1, mode = 'c'] log_nu_ai_buff = np.ascontiguousarray(log_nu_ai)
    cdef double * log_nu_ai_ptr = <double *> log_nu_ai_buff.data

    cdef double[:, :] result_view = result

    for ia in range(na):
        for isun in range(nsun):
            log_nu_ptr[ia * nsun + isun] = log(nu_range_ptr[ia * nsun + isun])

    cdef context cc
    cc.hp = hp
    cc.nsun = nsun
    cc.na = na
    cc.integrand = integrand_ptr
    cc.m_msun_ptr = m_msun_ptr
    cc.nu_range_ptr = nu_range_ptr
    cc.bias_ptr = bias_ptr
    cc.log_nu = log_nu_ptr
    cc.f_ptr = f_ptr
    cc.k_ptr = k_ptr
    cc.rv_mpc_ptr = rv_mpc_ptr
    cc.c_ptr = c_ptr

    if adaptive:
        for ia in range(na):
            for isun in range(nsun):
                log_nu_ai_ptr[isun] = log(nu_range_ptr[ia * nsun + isun])
            for ik in range(nk):
                _integrand_adaptive(ia, ik, cc)
                result_view[ik, ia] = trapez(log_nu_ai_ptr, integrand_ptr, nsun)
    else:
        for ia in range(na):
            for isun in range(nsun):
                log_nu_ai_ptr[isun] = log(nu_range_ptr[ia * nsun + isun])
            for ik in range(nk):
                _integrand_full(ia, ik, cc)
                result_view[ik, ia] = trapez(log_nu_ai_ptr, integrand_ptr, nsun)

    return result



@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)   # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef void _integrand_adaptive(size_t ia, size_t ik, context cc):

    cdef int isun_start, ii, feval = 0
    cdef size_t isun
    cdef double integrand_latest, i_left, i_right, current_max, remaining_int

    for isun in range(cc.nsun):
        cc.integrand[isun] = 0

    isun_start = 0
    current_max = 0.0
    for ii in range(NUM_SAMPLE):
        isun = (cc.nsun - 1) * ii / (NUM_SAMPLE - 1)
        integrand_latest = cc.integrand[isun] = integrand_at(ia, ik, isun, cc)
        if DEBUG_OUTPUT:
            print("sample at", isun, "is", integrand_latest)
        if integrand_latest > current_max:
            current_max = integrand_latest
            isun_start = isun
        feval += 1

    if DEBUG_OUTPUT:
        print("current max", current_max, "at", isun_start)

    cdef int il, ir
    cdef double log_nu_width = cc.log_nu[(ia + 1) * cc.nsun - 1] - cc.log_nu[ia * cc.nsun]

    il = ir = isun_start

    cdef double current_area = 0

    cc.integrand[il] = integrand_latest = integrand_at(ia, ik, il, cc)

    while il > 0:
        il -= 1
        cc.integrand[il] = i_left = integrand_at(ia, ik, il, cc)
        feval += 1
        if i_left < integrand_latest:
            break
        if DEBUG_OUTPUT:
            print("go left to peak", il, i_left)
        integrand_latest = i_left

    cc.integrand[ir] = integrand_latest = integrand_at(ia, ik, ir, cc)

    while ir < cc.nsun - 1:
        ir += 1
        cc.integrand[ir] = i_right = integrand_at(ia, ik, ir, cc)
        feval += 1
        if i_right < integrand_latest:
            break
        if DEBUG_OUTPUT:
            print("go right to peak", ir, i_right)
        integrand_latest = i_right

    while il >= 0 or ir < cc.nsun:

        if il >= 0:
            cc.integrand[il] = i_left = integrand_at(ia, ik, il, cc)
            if DEBUG_OUTPUT: print("left il", il, i_left)
            feval += 1

            if il < cc.nsun - 1:
                current_area += i_left * (cc.log_nu[ia * cc.nsun + il + 1] - cc.log_nu[ia * cc.nsun + il])

        if ir < cc.nsun:
            cc.integrand[ir] = i_right = integrand_at(ia, ik, ir, cc)
            if DEBUG_OUTPUT: print("left ir", ir, i_right)
            feval += 1
            if ir < cc.nsun - 1:
                current_area += i_right * (cc.log_nu[ia * cc.nsun + ir + 1] - cc.log_nu[ia * cc.nsun + ir])

        if il >= 0:
            remaining_int = i_left * (cc.log_nu[ia * cc.nsun + il] - cc.log_nu[ia * cc.nsun])
            if remaining_int / current_area < PRECISION:
                if DEBUG_OUTPUT: print("left", remaining_int / current_area)
                il = -1
            else:
                il -= 1

        if ir < cc.nsun:
            remaining_int = i_right * (cc.log_nu[(ia + 1) * cc.nsun - 1] - cc.log_nu[ia * cc.nsun + ir])
            if remaining_int / current_area < PRECISION:
                if DEBUG_OUTPUT: print("right", remaining_int / current_area)
                ir = cc.nsun
            else:
                ir += 1

    if DEBUG_OUTPUT: print("feval", feval)


@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)   # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef void _integrand_full(size_t ia, size_t ik, context cc) :

    cdef size_t isun

    for isun in range(cc.nsun):
        cc.integrand[isun] = integrand_at(ia, ik, isun, cc)


@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)   # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef inline double compute_ukm(size_t ia, size_t ik, size_t isun, context cc) :

    cdef double norm, krs, sik, cik, sick, cick
    cdef double term1, term2, term3, ukm
    cdef double rs_mpc_i, kimpc
    cdef double ci = cc.c_ptr[ia * cc.nsun + isun]

    kimpc = cc.k_ptr[ik]
    rs_mpc_i = cc.rv_mpc_ptr[ia * cc.nsun +  isun] / ci

    norm = log(1 + ci) - ci / (1 + ci)

    krs = kimpc * rs_mpc_i

    sici(krs, address(sik), address(cik))
    sici((1 + ci) * krs, address(sick), address(cick))
    term1 = cos(krs) * (cick - cik)
    term2 = + sin(krs) * (sick - sik)
    if krs == 0.0:
        term3 = -ci / (1 + ci)
    else:
        term3 = - sin(ci * krs) / ((1 + ci) * krs)
    ukm = (term1 + term2 + term3) / norm

    return ukm


@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)   # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef inline double integrand_at(size_t ia, size_t ik, size_t isun, context cc) :
    cdef double ukm, msun
    msun = cc.m_msun_ptr[isun]
    if isnan(msun):
        return 0.0

    if cc.hp == 1:
        ukm = compute_ukm(ia, ik, isun, cc)
    if cc.hp == 0:
        ukm = 1.0
    return ukm * cc.nu_range_ptr[ia * cc.nsun +  isun] * cc.f_ptr[ia * cc.nsun +  isun] * cc.bias_ptr[ia * cc.nsun + isun]
