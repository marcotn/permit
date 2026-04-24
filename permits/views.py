from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, RedirectView

from .document import generate_permit_docx
from .email import send_permit_email
from .forms import PermitFillForm, PermitRequestForm
from .models import PermitRequest


class StaffRequiredMixin(LoginRequiredMixin):
    """Redirect unauthenticated users to Google login; raise 403 for non-staff."""

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

class HomeView(RedirectView):
    pattern_name = "admin_panel"


# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------

class AdminPanelView(StaffRequiredMixin, ListView):
    model = PermitRequest
    template_name = "permits/admin_panel.html"
    context_object_name = "permits"

    def get_queryset(self):
        return PermitRequest.objects.select_related("created_by").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = PermitRequestForm()
        return ctx


class CreatePermitView(StaffRequiredMixin, View):

    def get(self, request):
        return redirect("admin_panel")

    def post(self, request):
        form = PermitRequestForm(request.POST)
        if form.is_valid():
            permit = form.save(commit=False)
            permit.created_by = request.user
            permit.save()
            try:
                send_permit_email(permit)
            except Exception as exc:
                messages.error(request, f"Permesso creato ma errore nell'invio email: {exc}")
            else:
                messages.success(request, _("Permesso creato e email inviata con successo."))

            if request.htmx:
                return self.render_to_htmx(request, form=PermitRequestForm(), show_success=True)
            return redirect("admin_panel")

        if request.htmx:
            return self.render_to_htmx(request, form=form)
        return self._render_panel(request, form)

    def render_to_htmx(self, request, form, show_success=False):
        from django.shortcuts import render
        permits = PermitRequest.objects.select_related("created_by").all()
        return render(request, "permits/partials/permit_list.html", {
            "permits": permits,
            "form": form,
            "show_success": show_success,
        })

    def _render_panel(self, request, form):
        from django.shortcuts import render
        return render(request, "permits/admin_panel.html", {
            "form": form,
            "permits": PermitRequest.objects.select_related("created_by").all(),
        })


# ---------------------------------------------------------------------------
# Public permit form (no login required)
# ---------------------------------------------------------------------------

class PermitFillView(View):

    def _get_permit(self, token):
        return get_object_or_404(PermitRequest, token=token)

    def get(self, request, token):
        from django.shortcuts import render
        permit = self._get_permit(token)
        if not permit.is_token_valid:
            return render(request, "permits/token_expired.html", status=410)
        if permit.is_completed:
            return render(request, "permits/already_filled.html", {"permit": permit})
        return render(request, "permits/permit_fill.html", {
            "form": PermitFillForm(),
            "permit": permit,
        })

    def post(self, request, token):
        from django.shortcuts import render
        permit = self._get_permit(token)
        if not permit.is_token_valid:
            return render(request, "permits/token_expired.html", status=410)
        if permit.is_completed:
            return render(request, "permits/already_filled.html", {"permit": permit})

        form = PermitFillForm(request.POST)
        if form.is_valid():
            permit.save_completed(**form.cleaned_data)
            template = "permits/partials/permit_done.html" if request.htmx else "permits/permit_done.html"
            return render(request, template, {"permit": permit})

        template = "permits/partials/fill_form.html" if request.htmx else "permits/permit_fill.html"
        return render(request, template, {"form": form, "permit": permit})


# ---------------------------------------------------------------------------
# Docx download
# ---------------------------------------------------------------------------

class PermitDocxView(View):

    VALID_TYPES = {"admin", "client"}


    def get(self, request, token, doc_type):
        if doc_type not in self.VALID_TYPES:
            raise Http404
        permit = get_object_or_404(PermitRequest, token=token, is_completed=True)
        docx_bytes = generate_permit_docx(permit, doc_type)
        label = "gestore" if doc_type == "admin" else "cliente"
        filename = f"permesso_{permit.permit_number}_{permit.permit_year}_{label}.docx"
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        response = HttpResponse(docx_bytes, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
