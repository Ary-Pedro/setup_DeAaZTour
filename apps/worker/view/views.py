from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.views import View
from django.core.mail import send_mail
import uuid
from .forms import RegisterForm
from apps.worker.models import CustomUser_Funcionario 
from setup_DeAaZTour import settings
User = get_user_model()

# INFO: Conta ----------------------------------------------------------------------------------------------------
# INFO: Campo de login da conta
def log(request):
    url_redefinir_senha = settings.BASE_URL + "/redefinirSenha/" #WARNING mudar lógica (em caso de deploy)

    if request.method == "POST":
        # Se o campo 'log' estiver presente, é uma tentativa de login
        if "log" in request.POST:
            log = request.POST.get("log")
            logpass = request.POST.get("logpass")
            user = authenticate(request, username=log, password=logpass)
            if user is not None:    #NOTE caso exista um usuário
                return redirect("home")

            elif(user.is_active == False): 
                    error_message = "Funcionário inativo"
                    return render(
                        request, "registro/login.html", {"error_message": error_message}
                    )
            else:
                error_message = "Apelido ou senha incorretos. Tente novamente."
                return render(
                    request, "registro/login.html", {"error_message": error_message}
                )
            
        # Se o campo '' estiver presente, é uma solicitação de recuperação de senha
        elif "email" in request.POST:
            email = request.POST.get("email")
            try:
                user = CustomUser_Funcionario.objects.get(email=email)
                user.token = str(uuid.uuid4())[:8]  # Apenas os 8 primeiros caracteres
                user.save()  # Salva o token no banco de dados

                send_mail(
                    subject="Relembrar senha",
                    message=f"Link de redefinição de senha: {url_redefinir_senha} \n\n Use o Token {user.token} para alterar seu acesso! \n\n Caso perca faça um novo pedido.",
                    from_email="projeto.abaprj@gmail.com",
                    recipient_list=[email],
                )
                return JsonResponse(
                    {
                        "message": "Um email com sua senha foi enviado para o endereço fornecido."
                    },
                    status=200,
                )
            except CustomUser_Funcionario.DoesNotExist:
                return JsonResponse({"message": "E-mail não encontrado."}, status=404)
            except Exception as e:
                return JsonResponse(
                    {
                        "message": "Ocorreu um erro ao enviar o e-mail. Por favor, tente novamente."
                    },
                    status=500,
                )

    return render(request, "login.html")

# INFO: Campo de registro da conta




# INFO: Campo de registro da conta
class RegisterView(TemplateView):
    template_name = "worker/registro.html"

    def get(self, request, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Criar o usuário
            user = CustomUser_Funcionario.objects.create_user(
                username=form.cleaned_data["log"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["logpass"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                cidade=form.cleaned_data["cidade"],
                telefone=form.cleaned_data["telefone"],
                cpf=form.cleaned_data["cpf"],
            )
            user.save()
            return redirect("log")
        else:
            # Mensagem de erro se o formulário for inválido
            return render(request, self.template_name, {"form": form})
        

# INFO: Redefinir senha da conta
def RedefinirSenha(request):
    if request.method == "POST":
        novolog = request.POST.get("log")
        novologpass = request.POST.get("logpass")
        novotoken = request.POST.get("token")

        # Verifica se todos os campos foram preenchidos
        if not all([novolog, novologpass, novotoken]):
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "email/email.html")

        try:
            # Tenta recuperar o usuário com o token fornecido
            user = CustomUser_Funcionario.objects.get(token=novotoken)

            # Verifica se o novo nome de usuário já está em uso
            if CustomUser_Funcionario.objects.filter(username=novolog).exists():
                messages.error(
                    request, "Esse nome de usuário já está em uso. Escolha outro."
                )
                return render(request, "email/email.html")

            # Redefine a senha e o nome de usuário
            user.set_password(
                novologpass
            )  # Usa set_password para criptografar a senha corretamente
            user.username = novolog
            user.token = None  # Remove o token após o uso
            user.save()

            messages.success(request, "Sua senha foi redefinida com sucesso.")
            return redirect(
                "homeAdmin"
            )  # Redireciona para a página de login ou onde preferir

        except CustomUser_Funcionario.DoesNotExist:
            messages.error(
                request, "Token inválido. Verifique o token enviado para o seu e-mail."
            )
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {str(e)}")

    # Se não for uma requisição POST, ou se a requisição POST não passar pelas verificações
    return render(request, "email/email.html")


# INFO: Sair da conta
class LogoutView(LogoutView):
    next_page = "log"

