# edgarapp/views.py

import itertools
from datetime import datetime
from django.contrib import messages

import requests
import textdistance
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
# For contact View
from django.http import HttpResponse, HttpResponseRedirect
# 404 error page
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from django.views.decorators.gzip import gzip_page
from django.views.generic import ListView, TemplateView

from .forms import ContactForm, UsersLoginForm, UsersRegisterForm
from .models import Company, Directors, Executives, Filing, Funds, Proxies
from .utils import TOCAlternativeExtractor


def handler404(request, *args, **argv):

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    response = render_to_response('404.html', {'extended_template': extended_template},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def HomePageView(request):
    template_name = 'home.html'

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def SearchResultsView(request):
    #model = Company, Filing, Funds, Directors, Proxies, Executives
    #template_name  = 'companyOverview.html'

    extended_template = 'base_company.html'
    if request.user.is_authenticated:
        extended_template = 'base_company_member.html'

    query = request.GET.get('q')
    print(query)



    if not request.user.is_authenticated:
        # print("done")
        if query != 'TSLA':
            messages.error(request,'To search for other Tickers,')
            return render(
            request, 'home.html',
            {'extended_template': extended_template}
            )
    mycompany = Company.objects.get(ticker=query)

    filing = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate').latest('filingdate');


    return HttpResponseRedirect('/filing/?q=' + query +'&fid='+str(filing.cik))

    #-------------no need to carry out the other searches as they are expensive-----------------------"
    # filings = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate')
    # proxies = Proxies.objects.filter(cik=mycompany.cik).order_by('-filingdate')
    # name = mycompany.name
    # name = name.upper()
    # name = name.replace('INTERNATIONAL', 'INTL')
    # name = name.replace(' /DE', '')
    # name = name.replace('/DE', '')
    # name = name.replace('INC.', 'INC')
    # name = name.replace(',', '')

    # matches = []
    # exectable = []

    # funds = Funds.objects.raw(
    #     'SELECT * FROM edgarapp_funds WHERE company = %s ORDER BY share_prn_amount+0 DESC LIMIT 100', [name])
    #
    # directors = Directors.objects.filter(
    #     company=mycompany.name).order_by('-director')
    #
    # allDirectors = Directors.objects.all()

    # executives = Executives.objects.filter(company=mycompany.name)
    # today = datetime.today()
    # currYear = today.year
    #
    # for year in executives:
    #     if year.filingdate.split('-')[0] == str(currYear):
    #         exectable.append(year)
    #
    # for person in directors:
    #     if person:
    #         personA = person.director.replace("Mr.", '')
    #         personA = person.director.replace("Dr.", '')
    #         personA = person.director.replace("Ms.", '')
    #         a = set([s for s in personA if s != "," and s != "." and s != " "])
    #         aLast = personA.split(' ')[-1]
    #         if (len(personA.split(' ')) == 1):
    #             aLast = personA.split('.')[-1]
    #     comps = []
    #     for check in allDirectors:
    #         if person:
    #             personB = check.director.replace("Mr.", '')
    #             personB = check.director.replace("Dr.", '')
    #             personB = check.director.replace("Ms.", '')
    #             bLast = personB.split(' ')[-1]
    #             if (len(personB.split(' ')) == 1):
    #                 bLast = personB.split('.')[-1]
    #             # print(personA, aLast, person.company, personB, bLast, check.company)
    #             if aLast == bLast:
    #                 # first check jaccard index to speed up algo, threshold of .65
    #                 b = set([s for s in personB if s !=
    #                          "," and s != "." and s != " "])
    #                 if (len(a.union(b)) != 0):
    #                     jaccard = float(
    #                         len(a.intersection(b)) / len(a.union(b)))
    #                 else:
    #                     jaccard = 1
    #                 # print(personA, personB, jaccard)
    #                 if (jaccard > 0.65):
    #                     # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
    #                     sequence = textdistance.ratcliff_obershelp(
    #                         personA, personB)
    #                     # print(sequence)
    #                     if sequence > 0.75 and mycompany.name != check.company:
    #                         comps.append(check.company)
    #     if not comps:
    #         comps.append('Director is not on the board of any other companies')
    #     matches.append(comps)
    #
    # object_list = []
    # object_list.append(query)
    # object_list.append((mycompany.name, mycompany.ticker))
    # object_list.append(filings)
    # object_list.append(funds)
    # object_list.append(zip(directors, matches))
    # object_list.append(zip(exectable, matches))
    # object_list.append(itertools.zip_longest(proxies, filings, fillvalue='foo'))

    # object_list is (q, (companyname, ticker), (filings object))
    # if request.user.is_authenticated:
    #print(object_list)

    latest_filing = []
    #for file in filings:


    # filing = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate').first()
    # print(filing)
    # url ='E:/Workspace/mblazr/edgarapp/static'+'/'+ 'filings/' + filing.filingpath
    # toc_extractor = TOCExtractor()
    # with open(url) as file:
    #
    #     filing_html = file.read()
    #
    #     try:
    #         extract_data = toc_extractor.extract(filing_html)
    #         table_of_contents = extract_data.table
    #     except:
    #        table_of_contents = ""
    #'filing_html': filing_html,'table_of_contents': table_of_contents


    #return render(
        #request, template_name,
        #{'object_list': object_list, 'extended_template': extended_template,
       #  'table_of_contents': table_of_contents,
      #   'filing_html': filing_html
     #    }
    #)
    # else:
    #     if query == 'HD':
    #         return render(
    #             request, template_name,
    #             {'object_list': object_list, 'extended_template': extended_template}
    #         )
    #     else:
    #         return render(request, 'about.html', {'extended_template': 'base.html'})


@gzip_page
def SearchFilingView(request):
    model = Company, Filing, Proxies
    template_name = 'companyFiling.html'

    extended_template = 'base_company.html'
    if request.user.is_authenticated:
        extended_template = 'base_company_member.html'

    matches = []
    exectable = []

   
    query = request.GET.get('q')
    fid = request.GET.get('fid')
    mycompany = Company.objects.get(ticker=query)

    #user is not logged in and
    # they are not searching for Tesla
    if not request.user.is_authenticated and query != 'TSLA' :
     #redirect them to login
         return redirect('/accounts/login/?next='+query)

    elif request.user.is_authenticated or ( not request.user.is_authenticated and query == 'TSLA') :
        #user is authenticated or they are not authenticated but are searching for Tesla
    #check if query sqtring has valid arguments
      if fid=='all':
        #query string fetches the latest filing

        filings = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate')
        filing = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate').latest('filingdate')
         # the latest filing is being recieved

      else:
        #normal fid is in place
        filings = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate')
        filing = Filing.objects.get(id=fid)  # the filing was requested by fid
      # page = open(url)
        # finder = filing.filingpath.split('/')[1]+"#"
        # soup = BeautifulSoup(page.read())
      links = []
      verify = []
      # for link in soup.find_all('a'):
      #   x = link.get('href')
      #   if str(x).startswith('https') or str(x).startswith('http'):
      #     if x.find('#') != -1:
      #       if link.string.find('Table of Contents') == -1 or x.endswith("#INDEX") == -1:
      #         # print(link.string.endswith("Index"))
      #         if link.string.endswith("Index") == False:
      #           # print('not present')
      #           if x in verify:
      #             for item in links:
      #               if x.find(item["url"]) != -1:
      #                 # print(link.string)
      #                 itemIndex = links.index(item)
      #                 # print("index", itemIndex)
      #                 del links[itemIndex]
        #                 store = {
        #                   "value": item["value"] + " " + link.string,
        #                   "url": item["url"]
        #                 }
        #                 links.append(store)
        #           else:
        #             # print('false')
        #             verify.append(x)
        #             store = {
        #               "value": link.string,
        #               "url": "#"+x.split('#')[1]
        #             }
        #             links.append(store)


      name = mycompany.name
      name = name.upper()
      name = name.replace('INTERNATIONAL', 'INTL')
      name = name.replace(' /DE', '')
      name = name.replace('/DE', '')
      name = name.replace('INC.', 'INC')
      name = name.replace(',', '')



      funds = Funds.objects.raw(
        'SELECT * FROM edgarapp_funds WHERE company = %s ORDER BY share_prn_amount+0 DESC LIMIT 100', [name])

      directors = Directors.objects.filter(
        company=mycompany.name).order_by('-director')

      allDirectors = Directors.objects.all()

      executives = Executives.objects.filter(company=mycompany.name)

      today = datetime.today()
      currYear = today.year

      for year in executives:
        if year.filingdate.split('-')[0] == str(currYear):
            exectable.append(year)

      for person in directors:
        if person:
            personA = person.director.replace("Mr.", '')
            personA = person.director.replace("Dr.", '')
            personA = person.director.replace("Ms.", '')
            a = set([s for s in personA if s != "," and s != "." and s != " "])
            aLast = personA.split(' ')[-1]
            if (len(personA.split(' ')) == 1):
                aLast = personA.split('.')[-1]
        comps = []
        for check in allDirectors:
            if person:
                personB = check.director.replace("Mr.", '')
                personB = check.director.replace("Dr.", '')
                personB = check.director.replace("Ms.", '')
                bLast = personB.split(' ')[-1]
                if (len(personB.split(' ')) == 1):
                    bLast = personB.split('.')[-1]
                # print(personA, aLast, person.company, personB, bLast, check.company)
                if aLast == bLast:
                    # first check jaccard index to speed up algo, threshold of .65
                    b = set([s for s in personB if s !=
                             "," and s != "." and s != " "])
                    if (len(a.union(b)) != 0):
                        jaccard = float(
                            len(a.intersection(b)) / len(a.union(b)))
                    else:
                        jaccard = 1
                    # print(personA, personB, jaccard)
                    if (jaccard > 0.65):
                        # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
                        sequence = textdistance.ratcliff_obershelp(
                            personA, personB)
                        # print(sequence)
                        if sequence > 0.75 and mycompany.name != check.company:
                            comps.append(check.company)
        if not comps:
             comps.append('Director is not on the board of any other companies')
        matches.append(comps)

        url = '/mnt/filings-static/capitalrap/edgarapp/static/filings/' + filing.filingpath

        object_list = []
        object_list.append((query, fid))
        object_list.append((mycompany.name, mycompany.ticker))
        object_list.append(filings)
        object_list.append(filing)
        object_list.append(funds)
        object_list.append(zip(directors, matches))
        object_list.append(zip(exectable, matches))
        object_list.append(links)

    t_o_c = filing.table_of_contents.first()
    
    if not t_o_c:

        toc_extractor = TOCAlternativeExtractor()
        
        extract_data = toc_extractor.extract(url)

        t_o_c = filing.table_of_contents.create(body=extract_data.table)

    with open(url) as file:
        filing_html = file.read()

    # object_list is ((q, fid), (companyname, name), (filings object), (filing))
    return render(
        request, template_name, {
            'object_list': object_list,
            'extended_template': extended_template,
            'table_of_contents': t_o_c.body,
            'filing_html': filing_html
        }
    )


def AboutView(request):
    template_name = 'about.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def HedgeFundView(request):
    template_name = 'hedgeFunds.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def FaqView(request):
    template_name = 'faq.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )

# for contact


def contactView(request):

    form = ContactForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    if form.is_valid():
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        message = form.cleaned_data.get("message")
        subject = "CapitalRap Contact Form: "+name

        comment = name + " with the email, " + email + \
            ", sent the following message:\n\n" + message
        send_mail(subject, comment, settings.EMAIL_HOST_USER,
                  [settings.EMAIL_HOST_USER])

        context = {'form': form, 'extended_template': extended_template}
        messages.info(request, 'Thank you for contacting us!')
        return HttpResponseRedirect(request.path_info)

    else:
        context = {'form': form, 'extended_template': extended_template}
        return render(
            request, 'contact.html', context,
        )

    # if request.method == 'GET':
    #    form = ContactForm()
    # else:
    #    form = ContactForm(request.POST)
    #    if form.is_valid():
    #        name = form.cleaned_data['name']
    #        email = form.cleaned_data['email']
    #        message = form.cleaned_data['message']
    #        try:
    #            send_mail('CapitalRap Contact Form '+name+' '+email, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
    #        except BadHeaderError:
    #            return HttpResponse('Invalid header found.') #TODO: ADD MESSAGE INSTEAD
    #        messages.info(request, 'Thank you for contacting us!')
    #        return HttpResponseRedirect(request.path_info)
    # return render(request, "contact.html", {'form': form})


##################
## Members side ##


def login_view(request):
    form = UsersLoginForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'home.html'

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)

        if request.GET.get('next') == None :
            return redirect('home')
        else:
            return redirect('/filing/?q='+request.GET.get('next') + '&fid=all')
    return render(request, "form.html", {
        "form": form,
        "title": "Login",
        'extended_template': extended_template,
    })


def register_view(request):
    form = UsersRegisterForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if request.GET.get('next') == None:
            return redirect('home')
        else:
            return redirect('/filing/?q=' + request.GET.get('next') + '&fid=all')

    return render(request, "form.html", {
        "title": "Register",
        "form": form,
        'extended_template': extended_template,
    })


@login_required
def account_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _(
                'Your password was successfully updated!'))
            return redirect('account')
        else:
            messages.error(request, _('There was an error. Try again!'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


def PlanView(request):
    return render(request, 'plan.html')
