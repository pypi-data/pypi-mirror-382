## find_element / find_elemetns
以下几种元素虽然在dom中但无法被找到，程序报错 （根据link_text选择除外）：
1. opacity == 0
2. visibility == 'hidden'
3. display == 'none'
4. position == 'absolute'，且位于屏幕外