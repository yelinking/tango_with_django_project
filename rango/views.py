from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    return render(request, 'rango/index.html', context=context_dict)
def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Linkun Ye'}
    return render(request, 'rango/about.html', context=context_dict)
def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context=context_dict)
@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})    
@login_required
def add_page(request,category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    if category is None:
        return redirect('/rango/')
        
        

    form = PageForm()
    
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                

                return redirect(reverse('rango:show_category',
                                            kwargs={'category_name_slug':
                                                    category_name_slug}))

        else:
             print(form.errors)      
    context_dict = {'form': form, 'category': category}

    
    return render(request, 'rango/add_page.html',context=context_dict)  


def register(request):
    # to tell the template whether the registration was successful:
    registered = False

    # if HTTP POST request, we are interested in processing form data:
    if request.method == 'POST':
        # attempt to grab info from the raw form info
        # NB: we make use of both UserForm and UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        # if the 2 forms are valid:
        if user_form.is_valid() and profile_form.is_valid():
            # save the user's form data to the database
            user = user_form.save()
            
            # hash the password with the set_password method then update the user object:
            user.set_password(user.password)
            user.save()
            
            # since we need to set the user attribute for UserProfile ourselves, set commit to False
            # This delays saving the model until we are ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user # we are only allowed to to this bc commit is False above
            
            # if user provided profile picture, get it from input form and put it in the UserProfile model:
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save UserProfile model instance:
            profile.save()
            
            # registration was successful:
            registered = True

        else:
            # invalid form or forms, mistakes or somthing else?
            print(user_form.errors, profile_form.errors)
            
    else:
        # no HTTP POST, so we render out form using 2 ModelForm instances
        # these forms will be blank, ready for user input:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request, 'rango/register.html', context={'user_form':user_form,
                                                           'profile_form':profile_form,
                                                           'registered':registered}) 
def user_login(request):
    if request.method == 'POST':
        # these info is obtained form the login form
        # request.POST.get('variable') as opposed to request.POST['variable']
        # request.POST.get('variable') returns None if the value does not exist while request.POST['variable'] will raise a KeyError exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use django's machinery to attempt to see if the username/password combination is valid
        # User object is returned if it is:        
        user = authenticate(username=username, password=password)

        # if we have a User object, the details are correct
        # if None, no user with matching credentails was found:
        if user:
            # is the account active? (it could be disabled)
            if user.is_active:
                # log user in by sending him to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # inactive account:
                return HttpResponse('Your Rango account is disabled.')
            
        else:
            # bad login details were provided:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    else:
        # the request is not not a HTTP POST, so display the login form:
        # no context dictionary to pass to the template
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
     return render(request, 'rango/restricted.html')
    
@login_required
def user_logout(request):
    # since we know the user is logged in, we can just log them out
    logout(request)
    return redirect(reverse('rango:index'))
    




    





