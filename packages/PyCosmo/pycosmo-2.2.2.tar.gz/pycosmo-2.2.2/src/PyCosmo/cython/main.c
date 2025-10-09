#include<stdio.h>

double sici(double, double*, double*);

int main()
{
    double r0, r1;
    sici(0.1, &r0, &r1);
    printf("%.15e\n", r0);
    printf("%.15e\n", r1);
}
