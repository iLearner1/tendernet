import django_filters
from django_filters.widgets import RangeWidget, SuffixedMultiWidget
from django_filters import DateFromToRangeFilter, RangeFilter
from lots.models import Article




class MyRangeWidget(RangeWidget):
    def __init__(self, from_attrs=None, to_attrs=None, attrs=None):
        super(MyRangeWidget, self).__init__(attrs)

        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)



class MyRangeWidget2(RangeWidget):
    def __init__(self, from_attrs=None, to_attrs=None, attrs=None):
        super(MyRangeWidget2, self).__init__(attrs)

        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)





class ArticleFilter(django_filters.FilterSet):
	date = DateFromToRangeFilter(widget=MyRangeWidget(
        from_attrs={'placeholder': 'Начало'},
        to_attrs={'placeholder': 'Конец'},
    ) )
	price = RangeFilter(widget=MyRangeWidget2(
        from_attrs={'placeholder': 'Начало'},
        to_attrs={'placeholder': 'Конец'},
    ))


	class Meta:
		model = Article
		fields = ('title','body','id', 'city','statzakup','date', 'price',)
