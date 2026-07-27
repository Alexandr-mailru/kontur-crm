from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ClientEditForm, ClientForm, DealForm, TaskForm
from .models import Client, Deal, Task
from .utils import safe_redirect


def _user_clients(user):
    return Client.objects.filter(owner=user)


def _user_deals(user):
    return Deal.objects.filter(owner=user).select_related('client')


@login_required
def dashboard(request):
    clients = _user_clients(request.user)
    deals = _user_deals(request.user)
    tasks = Task.objects.filter(owner=request.user, is_done=False).select_related('client', 'deal')[:8]

    stage_stats = deals.values('stage').annotate(count=Count('id')).order_by()
    pipeline = {row['stage']: row['count'] for row in stage_stats}
    won_sum = deals.filter(stage='won').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    pipeline_items = [(label, pipeline.get(key, 0)) for key, label in Deal.STAGE_CHOICES]

    return render(request, 'crm/dashboard.html', {
        'client_count': clients.count(),
        'deal_count': deals.count(),
        'open_deals': deals.exclude(stage__in=['won', 'lost']).count(),
        'won_sum': won_sum,
        'pipeline_items': pipeline_items,
        'recent_deals': deals[:6],
        'tasks': tasks,
        'today': date.today(),
    })


@login_required
def client_list(request):
    q = request.GET.get('q', '').strip()
    clients = _user_clients(request.user)
    if q:
        clients = clients.filter(Q(company__icontains=q) | Q(contact_name__icontains=q))
    return render(request, 'crm/client_list.html', {'clients': clients, 'q': q})


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        client = form.save(commit=False)
        client.owner = request.user
        client.save()
        messages.success(request, f'Клиент «{client.company}» добавлен.')
        return redirect('crm:client_detail', pk=client.pk)
    return render(request, 'crm/client_form.html', {'form': form, 'title': 'Новый клиент'})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(_user_clients(request.user), pk=pk)
    return render(request, 'crm/client_detail.html', {
        'client': client,
        'deals': client.deals.all(),
        'tasks': client.tasks.filter(is_done=False),
    })


@login_required
def client_edit(request, pk):
    client = get_object_or_404(_user_clients(request.user), pk=pk)
    form = ClientEditForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, 'Данные клиента обновлены.')
        return redirect('crm:client_detail', pk=client.pk)
    return render(request, 'crm/client_form.html', {'form': form, 'title': 'Редактирование клиента'})


@login_required
def deal_list(request):
    stage = request.GET.get('stage', '')
    deals = _user_deals(request.user)
    if stage and stage in dict(Deal.STAGE_CHOICES):
        deals = deals.filter(stage=stage)
    elif stage:
        stage = ''
    return render(request, 'crm/deal_list.html', {
        'deals': deals,
        'stage': stage,
        'stages': Deal.STAGE_CHOICES,
    })


@login_required
def deal_create(request):
    form = DealForm(request.POST or None)
    form.fields['client'].queryset = _user_clients(request.user)
    if form.is_valid():
        deal = form.save(commit=False)
        deal.owner = request.user
        deal.save()
        messages.success(request, 'Сделка создана.')
        return redirect('crm:deal_list')
    return render(request, 'crm/deal_form.html', {'form': form, 'title': 'Новая сделка'})


@login_required
@require_POST
def deal_stage(request, pk):
    deal = get_object_or_404(_user_deals(request.user), pk=pk)
    stage = request.POST.get('stage')
    if stage in dict(Deal.STAGE_CHOICES):
        deal.stage = stage
        deal.save(update_fields=['stage', 'updated_at'])
        messages.success(request, f'Этап: {deal.stage_label}')
    return safe_redirect(request, 'crm:deal_list')


@login_required
def task_list(request):
    show_done = request.GET.get('done') == '1'
    tasks = Task.objects.filter(owner=request.user).select_related('client', 'deal')
    if not show_done:
        tasks = tasks.filter(is_done=False)
    return render(request, 'crm/task_list.html', {'tasks': tasks, 'show_done': show_done})


@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    form.fields['client'].queryset = _user_clients(request.user)
    form.fields['deal'].queryset = _user_deals(request.user)
    if form.is_valid():
        task = form.save(commit=False)
        task.owner = request.user
        task.save()
        messages.success(request, 'Задача добавлена.')
        return redirect('crm:task_list')
    return render(request, 'crm/task_form.html', {'form': form, 'title': 'Новая задача'})


@login_required
@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task.objects.filter(owner=request.user), pk=pk)
    task.is_done = not task.is_done
    task.save(update_fields=['is_done'])
    return safe_redirect(request, 'crm:task_list')


def privacy(request):
    return render(request, 'legal/privacy.html')


def terms(request):
    return render(request, 'legal/terms.html')


def copyright_info(request):
    return render(request, 'legal/copyright.html')


def about(request):
    return render(request, 'legal/about.html')
