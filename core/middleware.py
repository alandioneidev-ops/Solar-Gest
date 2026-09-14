from .models import Auditoria


class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            try:
                Auditoria.objects.create(
                    usuario=request.user,
                    acao=request.method,
                    rota=request.path[:200],
                    descricao=f'{request.method} {request.path}'[:250],
                    metodo=request.method,
                    status_http=response.status_code,
                    ip=self._ip(request),
                )
            except Exception:
                pass
        return response

    @staticmethod
    def _ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')
