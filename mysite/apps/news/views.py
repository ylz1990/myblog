import json
import logging

from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404

# from haystack.views import SearchView as _SearchView

from mysite import settings
from news import models
from news import constants
from utils.json_fun import to_json_data
from utils.res_code import Code,error_map

logger = logging.getLogger('django')
# Create your views here.


class IndexView(View):
    """

    """
    def get(self,request):
        tags = models.Tag.objects.only("id","name").filter(is_delete=False)
        # context = {
        #     "tags":tags
        # }
        return render(request,"news/index.html",locals())




#  ajax 请求
# 传参   tag_id   page
# 后台的返回:  7 个字段
# 请求方式: GET
# /news/?tag_id=1&page=2
# url 查询字符


class NewsListView(View):
    """"""
    def get(self,request):
        # 1. 获取参数
        # 2. 校验参数
        try:
            tag_id = int(request.GET.get('tag_id',0))
        except Exception as e:
            logger.error("标签错误:\n{}".format(e))
            tag_id = 0
        try:
            page = int(request.GET.get('page',1))
        except Exception as e:
            logger.error("页码错误:\n{}".format(e))
            page = 1
        # 3. 从数据库拿数据
        # title ,digest , image_url , update_time ,  7字段   id
        # select_related  sql  inner join
        news_queryset = models.News.objects.select_related('tag','author').only('title','digest','image_url','update_time','tag__name','author__username')
        news = news_queryset.filter(is_delete=False,tag_id=tag_id) or news_queryset.filter(is_delete=False)
        # 4. 分页
        paginator = Paginator(news,constants.PER_PAGE_NEWS_COUNT)
        try :
            news_info = paginator.page(page)
        except EmptyPage:
            logger.error("用户访问的页数大于的总页数")
            news_info = paginator.page(paginator.num_pages)
        # 处理异常
        # 5.序列化输出
        news_info_list = []
        for n in news_info:
            news_info_list.append({
                'id':n.id,
                'title':n.title,
                'digest':n.digest,
                'image_url':n.image_url,
                'update_time':n.update_time.strftime('%Y年%m月%d日 %H:%M'),
                'tag_name':n.tag.name,
                'author':n.author.username
            })
        data ={
            'news':news_info_list,
            'total_pages':paginator.num_pages,
        }
        # 6. 返回数据前端
        return to_json_data(data=data)


# # 轮播图
# # 热门新闻
#
# # context   ajax
#
# class NewsBanner(View):
#     """"""
#     def get(self,request):
#         banners = models.Banner.objects.select_related('news').only('image_url','news_id','news__title').\
#             filter(is_delete=False).order_by('priority')[0:constants.SHOW_BANNER_COUNT]
#
#         # 序列化输出
#         banners_info_list = []
#         for b in banners:
#             banners_info_list.append(
#                 {
#                     'image_url':b.image_url,
#                     'news_id':b.news_id,
#                     'news_title':b.news.title
#                 }
#             )
#         data = {
#             'banners':banners_info_list
#         }
#         return to_json_data(data=data)
#
#
# # 文章详情
#
# #参数: news_id
# #  5  title author_username  update_time tag_name, content
#
#
# class NewsDetailView(View):
#     """
#     /news/<int:news_id>/
#     """
#     def get(self,request,news_id):
#         news = models.News.objects.select_related('tag','author').\
#             only('title','content','update_time','tag__name','author__username').\
#             filter(is_delete=False,id=news_id).first()
#         if news:
#             # content , update_time, parent.username parent.content ,parent.update_time
#             comments = models.Comments.objects.select_related('author','parent').\
#                 only('content','update_time','author__username','parent__content','parent__author__username','parent__update_time').filter(is_delete=False,news_id=news_id)
#
#             # 序列化输出
#             comments_list = []
#             for comm in comments:
#                 comments_list.append(comm.to_dict_data())
#             return render(request,'news/news_detail.html',locals())
#         else:
#             raise Http404('新闻{}不存在'.format(news_id))
#
# # news_id  URL
# # content
# # parent_id   可以不传
# # 当前用户?????  request.user
#
# class NewsCommentView(View):
#     """
#     /news/<int:news_id>/comments/
#     """
#     def post(self,request,news_id):
#         # 1.获取参数
#         # 2.校验参数
#         # 3.存入数据
#         # 4.返回给前端
#         if not request.user.is_authenticated:
#             return to_json_data(errno=Code.SESSIONERR,errmsg=error_map[Code.SESSIONERR])
#
#         if not models.News.objects.only('id').filter(is_delete=False,id=news_id).exists():
#             return to_json_data(errno=Code.PARAMERR,errmsg='新闻不存在')
#
#         json_data = request.body   # byte  str
#         if not json_data:
#             return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
#         dict_data = json.loads(json_data.decode('utf8'))
#
#         content = dict_data.get('content')
#         if not content:
#             return to_json_data(errno=Code.PARAMERR, errmsg="评论的内容不能为空")
#
#         # parent_id父评论的验证
#         # 1.有没有父评论
#         # 2.parent_id 必须数字
#         # 3.数据库里面是否存在parent_id
#         # 4.父评论的新闻id 是否跟news_id
#         parent_id = dict_data.get('parent_id')
#         try:
#             if parent_id:
#                 parent_id = int(parent_id)
#                 if not models.Comments.objects.only('id').filter(is_delete=False,id=parent_id,news_id=news_id).exists():
#                     return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
#         except Exception as e:
#             logger.info('前端传的parent_id异常{}'.format(e))
#             return to_json_data(errno=Code.PARAMERR, errmsg="未知异常")
#
#         # 保存到数据库
#         new_comment = models.Comments()
#         new_comment.content = content
#         new_comment.news_id = news_id
#         new_comment.author = request.user
#         new_comment.parent_id = parent_id if parent_id else None
#         new_comment.save()
#
#         return to_json_data(data=new_comment.to_dict_data())
#
#
#
#
# class SearchView(_SearchView):
#     # 模版文件
#     template = 'news/search.html'
#
#     # 重写响应方式，如果请求参数q为空，返回模型News的热门新闻数据，否则根据参数q搜索相关数据
#     def create_response(self):
#         kw = self.request.GET.get('q', '')
#         if not kw:
#             show_all = True
#             hot_news = models.HotNews.objects.select_related('news'). \
#                 only('news__title', 'news__image_url', 'news__id'). \
#                 filter(is_delete=False).order_by('priority', '-news__clicks')
#
#             paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
#             try:
#                 page = paginator.page(int(self.request.GET.get('page', 1)))
#             except PageNotAnInteger:
#                 # 如果参数page的数据类型不是整型，则返回第一页数据
#                 page = paginator.page(1)
#             except EmptyPage:
#                 # 用户访问的页数大于实际页数，则返回最后一页的数据
#                 page = paginator.page(paginator.num_pages)
#             return render(self.request, self.template, locals())
#         else:
#             show_all = False
#             qs = super(SearchView, self).create_response()
#             return qs
