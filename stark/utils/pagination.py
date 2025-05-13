"""
分页组件
"""


class Pagination(object):

    def __init__(self, current_page, all_count, base_url, query_params, per_page=10, paper_page_count=11):
        """
        分页初始化

        如果query_params传入的是dict对象
        可以通过 from urllib.parse import urlencode
        来将dict转化为所需要的格式

        :param current_page: 当前页码
        :param all_count: 数据库中总条数
        :param base_url: 基础url
        :param query_params: QueryDict对象url的get参数 使分页组件可以兼容list页面的搜索功能
        :param per_page: 每页显示数据条数
        :param paper_page_count: 页面上最多显示的页码数量
        """

        self.base_url = base_url
        self.query_params = query_params

        # 检验 数据如果传入的太小则返回第一页
        try:
            self.current_page = int(current_page)
            if self.current_page < 1:
                raise Exception()
        except Exception as e:
            self.current_page = 1

        self.per_page = per_page
        self.all_count = all_count
        self.paper_page_count = paper_page_count

        self.paper_count = (self.all_count + per_page - 1) // per_page

        self.half_paper_page_count = int(paper_page_count / 2)

    @property
    def start(self):
        """
        数据获取值起始索引
        :return:
        """
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """
        数据获取值结束索引
        :return:
        """
        return self.current_page * self.per_page

    def page_html(self):
        """
        生成HTML页码
        :return:
        """

        # 如果数据中页码 paper_count<11 paper_page_count
        if self.paper_count < self.paper_page_count:
            paper_start = 1
            paper_end = self.paper_count
        else:
            # 数据页码已超过11
            # 判断 如果当前页<=5 half_paper_count
            if self.current_page < self.half_paper_page_count:
                paper_start = 1
                paper_end = self.paper_page_count
            else:
                # 如果 当前页码+5 >总页码
                if (self.current_page + self.half_paper_page_count) > self.paper_count:
                    paper_end = self.paper_count
                    paper_start = self.paper_count - self.paper_page_count + 1
                else:
                    paper_start = self.current_page - self.half_paper_page_count
                    paper_end = self.current_page + self.half_paper_page_count
        page_list = []

        if self.current_page < 1:
            prev = '<li class="page-item"><a class="page-link" href="#">上一页</a></li>'
        else:
            self.query_params['page'] = self.current_page - 1
            prev = '<li class="page-item"><a class="page-link" href="%s?%s">上一页</a></li>' % (
                self.base_url, self.query_params.urlencode())

        page_list.append(prev)

        for i in range(paper_start, paper_end + 1):
            self.query_params['page'] = i
            if self.current_page == i:
                tpl = '<li class="page-item active"><a class="page-link" href="%s?%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), i)
            else:
                tpl = '<li class="page-item"><a class="page-link" href="%s?%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), i)
            page_list.append(tpl)

        if self.current_page >= self.paper_count:
            nex = '<li class="page-item"><a class="page-link" href="#">下一页</a></li>'
        else:
            self.query_params['page'] = self.current_page + 1
            nex = '<li class="page-item"><a class="page-link" href="%s?%s">下一页</a></li>' % (
                self.base_url, self.query_params.urlencode())

        page_list.append(nex)
        page_str = ''.join(page_list)

        return page_str
