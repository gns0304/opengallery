from django import forms
from django.core.validators import RegexValidator
from .models import ArtistApplication
from gallery.models import Artwork, Exhibition, ALLOWED_EXTENSIONS, ALLOWED_SIZE_MB
from django.core.exceptions import ValidationError
import os

PHONE_RE = r"^\d{3}-\d{3,4}-\d{4}$"

class ArtistApplicationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=16,
        label="이름",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "이름(최대 16자)"}),
    )
    birth_date = forms.DateField(
        label="생년월일",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": "YYYY-MM-DD"})
    )
    email = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "example@domain.com"})
    )
    phone = forms.CharField(
        label="연락처",
        validators=[RegexValidator(regex=PHONE_RE, message="연락처는 000-0000-0000 또는 000-000-0000 형식입니다.")],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "010-1234-5678"})
    )

    class Meta:
        model = ArtistApplication
        fields = ["name", "gender", "birth_date", "email", "phone"]
        widgets = {
            "gender": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "gender": "성별"
        }

class ArtworkCreateForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ["title", "price", "size", "image"]
        labels = {
            "title": "작품 제목",
            "price": "작품 가격",
            "size": "작품 호수",
            "image": "작품 이미지",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": 64,
                "placeholder": "작품 제목",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "id": "price-input",
                "placeholder": "숫자만 입력",
                "inputmode": "numeric",
            }),
            "size": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 500,
                "placeholder": "1 ~ 500까지의 호수",
                "inputmode": "numeric",
            }),
        }

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise ValidationError("작품의 제목을 입력해주세요.")
        if len(title) > 64:
            raise ValidationError("작품의 제목은 64자 이하로 입력해주세요.")
        return title

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            raise ValidationError("작품의 가격을 입력해주세요.")
        if price < 0:
            raise ValidationError("작품의 가격은 0 이상의 정수여야 합니다.")
        return price

    def clean_size(self):
        size = self.cleaned_data.get("size")
        if size is None:
            raise ValidationError("작품의 호수를 입력해주세요.")
        if size < 1 or size > 500:
            raise ValidationError("작품의 호수는 1 이상 500 이하의 정수여야 합니다.")
        return size

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(f"허용된 이미지 형식이 아닙니다: {', '.join(ALLOWED_EXTENSIONS)}")

            if image.size > ALLOWED_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"이미지 파일 크기는 {ALLOWED_SIZE_MB}MB 이하만 가능합니다.")
        return image

class ExhibitionCreateForm(forms.ModelForm):

    class Meta:
        model = Exhibition
        fields = ["title", "start_date", "end_date", "artworks", "image"]
        labels = {
            "title": "전시 제목",
            "start_date": "전시 시작일",
            "end_date": "전시 종료일",
            "artworks": "전시 작품 목록",
            "image": "전시 이미지",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": 64,
                "placeholder": "전시 제목",
            }),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "placeholder": "YYYY-MM-DD",
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "placeholder": "YYYY-MM-DD",
            }),
            "artworks": forms.SelectMultiple(attrs={"class": "form-select d-none"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            profile = getattr(self.user, "artistprofile", None)
            self.fields["artworks"].queryset = (
                Artwork.objects.filter(artist=profile).order_by("-id") if profile else Artwork.objects.none()
            )
        else:
            self.fields["artworks"].queryset = Artwork.objects.none()

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise ValidationError("전시 제목을 입력해주세요.")
        if len(title) > 64:
            raise ValidationError("전시 제목은 64자 이하로 입력해주세요.")
        return title

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(f"허용된 이미지 형식이 아닙니다: {', '.join(ALLOWED_EXTENSIONS)}")

            if image.size > ALLOWED_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"이미지 파일 크기는 {ALLOWED_SIZE_MB}MB 이하만 가능합니다.")
        return image

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        arts = cleaned.get("artworks")

        if start and end and end < start:
            self.add_error("end_date", ValidationError("전시 종료일은 시작일 이후여야 합니다."))
        if not arts or len(arts) == 0:
            self.add_error("artworks", ValidationError("전시 작품을 최소 1개 이상 선택하세요."))
        else:
            profile = getattr(self.user, "artistprofile", None)
            invalid_arts = arts.exclude(artist=profile)
            if invalid_arts.exists():
                self.add_error("artworks", ValidationError("본인 소유의 작품만 선택할 수 있습니다."))

        return cleaned