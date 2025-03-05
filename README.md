### 引言/动机

项目需要给定一个任务区域, 快速索引该区域所涉及的S-57海图. 如果要对海图库中所有海图的有效区域分别求交集是否为空, 无疑是复杂的, shapely库预置的多边形求交计算, 似乎可能生成不合法图形, 还需逐个判断. 本人思路为, 通过空间复杂度换时间复杂度. 即, 预先求取所有海图的最小覆盖圆的圆心和半径并存储, 随后多边形求交集问题即可粗略的变为(前者是后者的充分条件)求圆是否相交的问题, 而此问题只需要计算圆心距离, 再和两圆半径进行比较即可.  

### 海图的覆盖范围

可读取M_COVR图层获取S-57海图的覆盖范围, 此处摘录M_COVR的定义如下:  

```
A geographical area that describes the coverage and extent of spatial objects.
```

### 最小圆求解算法

参考: https://en.wikipedia.org/wiki/Smallest-circle_problem  
及: https://www.sunshine2k.de/coding/java/Welzl/Welzl.html  

本例采用Welzl’s Algorithm.  

>The initial input is a set P of points. The algorithm selects one point p randomly and uniformly from P, and recursively finds the minimal circle containing P – {p}, i.e. all of the other points in P except p. If the returned circle also encloses p, it is the minimal circle for the whole of P and is returned.  
>Otherwise, point p must lie on the boundary of the result circle. It recurses, but with the set R of points known to be on the boundary as an additional parameter.  
>The recursion terminates when P is empty, and a solution can be found from the points in R: for 0 or 1 points the solution is trivial, for 2 points the minimal circle has its center at the midpoint between the two points, and for 3 points the circle is the circumcircle of the triangle described by the points. (In three dimensions, 4 points require the calculation of the circumsphere of a tetrahedron.)  
>Recursion can also terminate when R has size 3 (in 2D, or 4 in 3D) because the remaining points in P must lie within the circle described by R.  

伪代码如下:  

```c++
/*
 * Calculates the sed of a set of Points. Call initially with R = empty set.
 * P is the set of points in the plane. R is the set of points lying on the boundary of the current circle.
 */

function sed(P,R)
{
    if (P is empty or |R| = 3) then
         D := calcDiskDirectly(R)
    else
        choose a p from P randomly;
        D := sed(P - {p}, R);
        if (p lies NOT inside D) then
            D := sed(P - {p}, R u {p});
    return D;
}
```

#### 三点求圆

需要用到以下核心公式:  

$$
sin \theta = \frac{|a \times b|}{|a||b|}
$$

正弦定理:  

$$
\frac{a}{sinA} = \frac{b}{sinB} = \frac{c}{sinC} = 2R = D
$$

### 性能分析

见viztracer文件. 使用上述方法判断, 运算时间约3ms. 如果逐个读取海图文件, unary_union相关图层, 再判断是否相交, 性能瓶颈主要在读取和unary_union, 总运算时间为十秒级.  