#include <stdlib.h>
#include <queue>
#include <iostream>
#include <string>
#include <stdio.h>
//#include <tchar.h>
#include <assert.h>
#include <omp.h>
#include <algorithm>
#include <map>
#include <mex.h>
#include <bitset> //a^=b is the bitwise xor assign operator

#include <iostream>
#include <emmintrin.h>
#include <inttypes.h>

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
    //The input arrays are uint8
    //The descriptor size is 32 bytes
    
    unsigned int numBytes = mxGetM(prhs[0]);
    if (numBytes!=32)
    {
        mexPrintf("Only supports 32 byte descriptors\n");
        return;
    }
    unsigned char *qry = (unsigned char*)mxGetData(prhs[0]);
    
    unsigned int N = mxGetN(prhs[1]); // there are N database items
    unsigned char *arr = (unsigned char*)mxGetData(prhs[1]);
    
    plhs[0] = mxCreateNumericMatrix(N, 1, mxUINT16_CLASS, mxREAL);
    unsigned short *out = (unsigned short*)mxGetData(plhs[0]);
    
    for (int i = 0 ; i < N*32; i+=32)
    {
        __m128i cmp;
        unsigned char cmp_[16];
         uint64_t cnt = 0, cmp0 = 0, cmp1 = 0;
        
        __m128i arr0 = _mm_loadu_si128( reinterpret_cast<__m128i*>( arr + i ) );
        __m128i qry0 = _mm_loadu_si128( reinterpret_cast<__m128i*>( qry + 0 ) );
        cmp = _mm_xor_si128(arr0, qry0);
        _mm_storeu_si128(reinterpret_cast<__m128i*>(cmp_), cmp);
        cmp0 = *(reinterpret_cast<unsigned uint64_t *>(cmp_));
        cmp1 = *(reinterpret_cast<unsigned uint64_t *>(cmp_ + 8));
        cnt = __popcnt64(cmp0) + __popcnt64(cmp1);
        
        arr0 = _mm_loadu_si128( reinterpret_cast<__m128i*>( arr + i + 16 ) );
        qry0 = _mm_loadu_si128( reinterpret_cast<__m128i*>( qry + 16 ) );
        cmp = _mm_xor_si128(arr0, qry0);
        _mm_storeu_si128(reinterpret_cast<__m128i*>(cmp_), cmp);
        cmp0 = *(reinterpret_cast<unsigned uint64_t *>(cmp_));
        cmp1 = *(reinterpret_cast<unsigned uint64_t *>(cmp_ + 8));
        cnt += __popcnt64(cmp0) + __popcnt64(cmp1);
        
        out[i/32] = cnt;
    }

}