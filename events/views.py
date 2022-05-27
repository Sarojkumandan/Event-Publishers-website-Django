from multiprocessing import context
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import NewUserForm, NewOrganizerForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
#from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Q
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from django.contrib.auth import get_user_model
User = get_user_model()

geocoder = Nominatim(user_agent = 'events')
geocode = RateLimiter(geocoder.geocode, min_delay_seconds = 1,   return_value_on_exception = None)
# after initiating geocoder
#location = geocode(address)
# returns location object with longitude, latitude and altitude instances
#(location.latitude, location.longitude)

# Create your views here.


def home(request):
    context={
       'posts':Post.objects.all()
    }
    return render(request,'home.html',context)

class PostListView(ListView):
	model = Post
	template_name= 'home.html'
	context_object_name = 'posts'

class PostDetailedView(LoginRequiredMixin, DetailView):
	login_url = '/login/'
	model = Post
	template_name= 'view.html'
	def get_context_data(self, **kwargs):
		context = super(PostDetailedView, self).get_context_data(**kwargs)
		post=get_object_or_404(Post, id=self.kwargs['pk'])
		is_liked=False
		if post.favourite.filter(id=self.request.user.id).exists():
			is_liked=True
		loc=context['object'].location
		y=loc.split(',')
		for i in range(len(y)):
			x=geocode(''.join(y[i:]))
			if x!=None:
				break
		if x==None:
			x=geocode('india')
			
		setattr(context['object'],'long',x.longitude)
		setattr(context['object'],'lang',x.latitude)
		context['is_liked']=is_liked

		return context

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
	login_url = '/login/'
	model = Post
	fields = ['event_name', 'image_link','description','category','location','event_date', 'register_link']
	template_name = 'new_post.html'

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)
	
	def test_func(self):
		if self.request.user.is_superuser or self.request.user.is_organizer:
			return True
		return False

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['event_name','image_link','description','category','location','event_date','register_link']
	template_name = 'new_post.html'

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)
	
	def test_func(self):
		post=get_object_or_404(Post, id=self.kwargs['pk'])
		if self.request.user.is_superuser or self.request.user == post.author:
			return True
		return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	template_name = 'post_delete.html'
	success_url = '/'
	def test_func(self):
		if self.request.user.is_superuser or self.request.user.is_organizer:
			return True
		return False

class SearchResultsView(LoginRequiredMixin, ListView):
	login_url='/login/'
	model = Post
	template_name = "search_results.html"

	def get_queryset(self):
		query = self.request.GET.get("q").capitalize()
		object_list = Post.objects.filter(
			Q(location__icontains=query) | Q(category__icontains=query) | Q(event_date__icontains=query) | Q(event_name__icontains=query)
		)
		return object_list



def about(request):
    return render(request,'about.html',{'title':'About'})

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("/")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form,'title':'Register'})

def register_organizer(request):
	if request.method == "POST":
		form = NewOrganizerForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("/")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register_organizer.html", context={"register_form":form,'title':'Register Organizer'})


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None and user.is_user:
				login(request, user)
				messages.success(request, f"You are now logged in as {username}.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form,'title':'Login'})


def login_organizer(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None and user.is_organizer:
				login(request, user)
				messages.success(request, f"You are now logged in as {username} - Organizer.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login_organizer.html", context={"login_form":form,'title':'Login for Organizer'})

def login_admin(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None and user.is_superuser:
				login(request, user)
				messages.success(request, f"You are now logged in as {username} - Organizer.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login_admin.html", context={"login_form":form,'title':'Login for Admin'})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/")


def favourite_post(request,pk):
	post=get_object_or_404(Post, id=pk)
	if post.favourite.filter(id=request.user.id).exists():
		post.favourite.remove(request.user)
	else:
		post.favourite.add(request.user)
	return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))

def post_favourites(request):
	user = request.user
	fav_posts=user.favourite.all()
	context={
		'fav_posts':fav_posts,
		'title':"Favourites"
	}
	return render(request,'fav_posts.html',context)

def my_events(request):
	posts = Post.objects.filter(author=request.user)
	context={
		'fav_posts':posts,
		'title':"My Events"
	}
	return render(request,'my_events.html',context)

def list_users(request):
	posts=Post.objects.all()
	context={
		'users':User.objects.all(),
		'posts':posts,
		'title':"Users"
	}
	if(request.user.is_superuser):
		return render(request,'users.html',context)
	else:
		return redirect('/login')

def del_user(request, username):
	try:
		u=User.objects.get(username=username)
		if(request.user.is_superuser):
			u.delete()
			messages.success(request, "The user is deleted successfully")
			#return render(request, 'users.html')
		else:
			messages.error(request, 'Only admin has such permissions!!')
	except User.DoesNotExist:
		messages.error(request, 'User doesnt exist!!')
		return render(request, 'users.html')
	except Exception as e:
		return render(request, 'users.html',{'err':e.message})
	
	return render(request, 'users.html')