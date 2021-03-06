---
title: 使用Scrapy时提取一个块级标签下的所有文本的正确方式
date: 2021-04-05 13:33:46
tags:
  - Python
  - Scrapy
categories:
  - 网络爬虫
---

使用 Scrapy 爬取一篇博客的内容([原文链接](https://www.cnblogs.com/flashsun/p/14266148.html))，这里忽略正文中的图片，只针对文本内容。

博客正文内容位于标签：

```html
<div id="cnblogs_post_body" class="blogpost-body blogpost-body-html">
  <p>
    <span>
      <strong>你是</strong>
      <strong>一台电脑，你的名字叫 A</strong>
    </span>
  </p>
  <p>...</p>
  <p>
    <span>
      如果你纠结，要么去研究一下操作系统是如何处理网络 IO
      的，要么去研究一下包是如何被网卡转换成电信号发送出去的，要么就仅仅把它当做电脑里有个小人在
      <strong>开枪</strong>
      吧~
    </span>
  </p>
  <p>...</p>
  <p>...</p>
  <h1>第三层</h1>
  <p>...</p>
  ...... ......
</div>
```

可见，正文内容内部的结构比较复杂，没有一致可循的规律，那么怎样提取其中所有的文本内容呢？

<!-- more -->

第一步，先选择 id=cnblogs_post_body 的 div 标签，

```html
<div id="cnblogs_post_body" class="blogpost-body blogpost-body-html">...</div>
```

打开终端，使用 Scrapy Shell 测试，

```bash
 scrapy shell https://www.cnblogs.com/flashsun/p/14266148.html
```

```bash
>>> post_body=response.xpath('//div[@id="cnblogs_post_body"]')
>>> post_body
>>> [<Selector xpath='//div[@id="cnblogs_post_body"]' data='<div id="cnblogs_post_body" class="bl...'>]
```

然后，尝试使用 text()和 getall()获取所有文本：

```bash
>>> post_body.xpath('.//text()').getall()
>>> ['\n', '\xa0', '\n', '你是', '一台电脑，你的名字叫 A', '\n', '\xa0', '\n', '很久很久之前，你不与任何其他电脑相连接，孤苦伶仃。', '\n', '\n', '直到有一天，你
希望与另一台电脑 B 建立通信，于是你们各开了一个网口，用一根', '网线', '连接了起来。', '\n', '\n', '\xa0', '\n', '用一根网线连接起来怎么就能"通信"了呢？我可以给你讲 IO、讲中断、讲缓冲区，但这不是研究网络时该关心的问题。', '\n', '如果你纠结，要么去研究一下操作系统是如何处理网络 IO 的，要么去研究一下包是如何被网卡转换成电信号发送出去的，要么就仅仅把它当做电脑里有个小人在', '开枪', '吧~', '\n', '\n', '反正，你们就是连起来了，并且可以通信。', '\n', '\xa0', '\n', '第一层', '\n', '\xa0', '\n', '有一天，一个新伙伴 C 加入了，但聪明的你们很快发现，可以每个人开', '两个网口', '，用一共', '三根网线', '，彼此相连。', '\n', '\n', '随着越来越多的人加入，你发现身上开的网口实在太多了，而且网线密密麻麻，混乱不堪。（而实际上一台电脑根本开不了这么多网口，所以这种连线只在理论上可行，所以连不上的
我就用红色虚线表示了，就是这么严谨哈哈~）', '\n', '\n', '于是你们发明了一个中间设备，你们将网线都插到这个设备上，由这个设备做转发，就可以彼此之间通信了，本质上和原来一样，只不过网口的数量和网线的数量减少了，不再那么混乱。', '\n', '\n', '你给它取名叫', '集线器', '，它仅仅是无脑将电信号', '转发到所有出口（广播）', '，不做任何处理，你觉得它是没有智商的，因此把人家定性在了', '物理层', '。', '\n', '\xa0', '\n', '由于转发到了所有出口，那 BCDE 四台机器怎么知道数据包是不是发给自己的呢？', '\n', '首先，你要给所有的连接到交换机的设备，都起个名字。原来你们叫 ABCD，但现在需要一个更专业的，', '全局唯一', '的名字作为标识，你把这个更高端的名字称为\xa0', 'MAC 地址', '。', '\n', '你的 MAC 地址是 aa-aa-aa-aa-aa-aa，你的伙伴 b 的 MAC 地址是 bb-bb-bb-bb-bb-bb，以此类推，不重复就好。', '\n', '这样，A 在发送数据包给 B 时，只要在头部拼接
......
......
......]
```

得到结果是一个所有文本的列表，或者说是当前 div 元素下所有文本节点的集合，那么怎样才能将结果拼接成一篇完整的博客内容呢？

最直接暴力的办法当然是通过循环迭代将列表中所有元素拼接起来，这里不在赘述。其实在 XPath 中原生提供了 string()函数来转换字符串，下面尝试使用：

```bash
>>> post_body.xpath('string(.//text())').getall()
>>> ['\n']
```

什么鬼？！好好的一大篇文章就剩下一个换行......

一开始我也只好倒回去老老实实写 for...in...，直到后来翻看官方文档才找到问题所在：

> When you need to use the text content as argument to an XPath string function, avoid using .//text() and use just . instead.

当我们使用.//text()时，所得到的是一个 node-set，把一个 node-set 传递给 string()进行字符串转换的时候，只会作用于 node-set 中的第一个元素，类似的情况还有使用 contains()和 starts-width()，而这里 post_body 中的第一个元素正好就是"\n"！

而如果将一个 node 进行字符串转换，就会将该节点以及其子孙节点中的文本进行拼接，因此在这个例子中，我们因该直接对 post_body 使用 string()：

```bash
>>> post_body.xpath('string(.)').getall()
>>> ['\n\xa0\n你是一台电脑，你的名字叫 A\n\xa0\n很久很久之前，你不与任何其他电脑相连接，孤苦伶仃。\n\n直到有一天，你希望与另一台电脑 B 建立通信，于是你们各开了一个网口，用一根网线连接了起来。\n\n\xa0\n用一根网线连接起来怎么就能"通信"了呢？我可以给你讲 IO、讲中断、讲缓冲区，但这不是研究网络时该关心的问题。\n如果你纠结，要么去研究一下操作系统是如何处理网络 IO 的，要么去研究一下包是如何被网卡转换成电信号发送出去的，要么就仅仅把它当做电脑里有个小人在开枪吧~\n\n反正，你们就是连起来了，并且可以通信。\n\xa0\n第一层\n\xa0\n有一天，一个新伙伴 C 加入了，但聪明的你们很快发现，可以每个人开两个网口，用一共三根网线，彼此相连。\n\n随着越来越多的人加入，你发现身上开的网口实在太多了，而且网线密密麻麻，混乱不堪。（而实际上一台电脑根本开不了这么多网口，所以这种连线只在理论上可行，所以连不上的我就
用红色虚线表示了，就是这么严谨哈哈~）\n\n于是你们发明了一个中间设备，你们将网线都插到这个设备上，由这个设备做转发，就可以彼此之间通信了，本质上和原来一样，只不过网口的数量和网线的数量减少了，不再那么混乱。\n\n你给它取名叫集线器，它仅仅是无脑将电信号转发到所有出口（广播），不做任何处理，你觉得它是没有智商的，因此
把人家定性在了物理层。\n\xa0\n由于转发到了所有出口，那 BCDE 四台机器怎么知道数据包是不是发给自己的呢？\n首先，你要给所有的连接到交换机的设备，都起个名字。原
来你们叫 ABCD，但现在需要一
......
......
，于是收下了这个包\n\xa0\n更详细且精准的过程：\n读到这相信大家已经很累了，理解上述过程基本上网络层以下的部分主流程就基本疏通了，如果你想要本过程更为专业的过程描述，可以在公众号 低并发编程 后台回复 网络，获得我模拟这个过程的 Cisco Packet Tracer 源文件。\n\n每一步包的传输都 会有各层的原始数据，以及专业的过程描述\n\n\xa0\n\xa0\n同时在此基础之上你也可以设计自己的网络拓扑结构，进行各种实验，来加深网络传输过程的理解。\n\xa0\n后记\n\xa0\n至此，经过物理层、数据链路层、网络层这前三层的协议，以及根据这些协议设计的各种网络设备（网线、集线器、交换机、路由器），理论上只要拥有对方的 IP 地址，就已经将地球上任意位置的两个节点连通了。\n\n本文经过了很多次的修改，删减了不少影响主流程的内容，就是为了让读者能抓住网络传输前三层的真正核心思想。同时网络相关 的知识也是多且杂，我也还有很多搞不清楚的地方，非常欢迎大家与我交流，共同进步。\n']
```

哈哈，这次终于正确返回了一篇完整的博客文本内容！当然，在这里我们可以直接使用 get()而不是 getall()，因为 string(.)会自动将当前节点和其子孙节点的文本进行拼接，这样就可以获得一个字符串方便直接使用。

在官方文档中还列举了一个使用 contains()对节点文本内容进行匹配的例子：

```bash
>>> from scrapy import Selector
>>> sel=Selector(text='<a href="#">Click here to go to the <strong>Next Page</strong></a>')
>>> sel.xpath('//a[contains(.//text(),'Next Page')]').getall()
>>> []
>>> sel.xpath('//a[contains(.,'Next Page')]').getall()
>>> ['<a href="#">Click here to go to the <strong>Next Page</strong></a>']
```

使用.//text()时，得到的结果其实只有 a 中的第一个文本节点，即："Click here to go to the "，因此无法匹配文本"Next Page"，而使用节点本身，得到的是当前节点和其子孙节点的所有文本内容的拼接，即："Click here to go to the Next Page"，因此成功匹配。

最后，放上 Scrapy 官方文档中，本文相关内容的[链接](https://docs.scrapy.org/en/latest/topics/selectors.html#using-text-nodes-in-a-condition)
