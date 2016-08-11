from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _
from account.models import CustomUser
from college.models import College, Stream
from student.models import Student, Qualification, TechProfile
from urllib.parse import urlparse
import re

class StudentLoginForm(forms.Form):
	username = forms.CharField(label=_('Enrollment Number'), max_length=11, widget=forms.TextInput(attrs={'placeholder': _('or email address'), 'auto_focus':''}))
	password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'placeholder':_('Enter Password')}))

	def __init__(self, *args, **kwargs):
		self.user_cache = None
		super(StudentLoginForm, self).__init__(*args, **kwargs)

	def clean(self, *args, **kwargs):
		super(StudentLoginForm, self).clean(*args, **kwargs)
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if username and password:
			queryset = CustomUser.objects.filter(type='S').filter(is_superuser=False)
			if '@' in username:
				try:
					student = queryset.get(email=username)
					username = student.username
				except CustomUser.DoesNotExist:
					raise forms.ValidationError(_('Student with this email address does not exist'))
			else:
				try:
					queryset.get(username=username)
				except CustomUser.DoesNotExist:
					raise forms.ValidationError(_('Invalid enrollment number'))
			self.user_cache = authenticate(username=username, password=password)
			if self.user_cache is None:
				raise forms.ValidationError(_('Invalid enrollment number or password'))
		return self.cleaned_data
	
	def get_user(self):
		return self.user_cache

class StudentSignupForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(StudentSignupForm, self).__init__(*args, **kwargs)
		self.fields['email'].required = True
		self.fields['username'].widget.attrs['maxlength'] = 11
		self.fields['username'].validators = [validators.RegexValidator(r'^\d{11}$')]
	
	password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'placeholder': _('Enter password')}))
	password2 = forms.CharField(label=_('Re-enter Password'), widget=forms.PasswordInput(attrs={'placeholder': _('Confirm password')}))

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			roll, coll, strm, year = re.match(r'^(\d{3})(\d{3})(\d{3})(\d{2})$', username).groups()
		except AttributeError:
			raise forms.ValidationError(_('Enrollment number should contain only digits'))
		except ValueError:
			raise forms.ValidationError(_('Enrollment number should be 11 digits long'))
		if College.objects.filter(code=coll).count() == 0:
			raise forms.ValidationError(_('Institution with code %s does not exist' % coll))
		if Stream.objects.filter(code=strm).count() == 0:
			raise forms.ValidationError(_('Incorrect programme code'))
		if not College.objects.get(code=coll).streams.filter(code=strm).exists():
			raise forms.ValidationError(_('Invalid enrollment number'))
		return username

	def clean(self, *args, **kwargs):
		super(StudentSignupForm, self).clean(*args, **kwargs)
		pwd1 = self.cleaned_data['password1']
		pwd2 = self.cleaned_data['password2']
		if pwd1 and pwd2 and pwd1!=pwd2:
			raise forms.ValidationError(_('Passwords must match.'))
		return self.cleaned_data

	def save(self, commit=True, *args, **kwargs):
		student = super(StudentSignupForm, self).save(commit=False)
		student.set_password(self.cleaned_data['password2'])
		student.is_active = False
		student.type = 'S'
		if commit:
			try:
				student.save()
			except IntegrityError:
				raise forms.ValidationError(_('Student already exists'))
			except ValidationError as error:
				raise forms.ValidationError(error)
		return student

	class Meta:
		model = CustomUser
		fields = ['username', 'email']
		labels = {'username': _('Enrollment Number')}
		help_texts = {
			'username': _('Enter your 11 digit enrollment number.'),
			'email': _('An activation email will be sent to the registered email address.'),
		}

class StudentCreationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.user_profile = kwargs.pop('profile', None)
		self.coll = kwargs.pop('coll', None)
		self.strm = kwargs.pop('strm', None)
		super(StudentCreationForm, self).__init__(*args, **kwargs)
		self.fields['phone_number'].required = False
		self.initial['college'] = self.coll
		self.initial['stream'] = self.strm
		self.initial['programme'] = Stream.objects.get(pk=self.strm).programme.pk
		self.fields['college'].widget.attrs['disabled'] = 'disabled'
		self.fields['stream'].widget.attrs['disabled'] = 'disabled'
		self.fields['programme'].widget.attrs['disabled'] = 'disabled'

	def clean_college(self):
		college = self.cleaned_data['college']
		if college and college.pk != self.coll:
			raise forms.ValidationError(_('Error. College field changed.'))
		return college

	def clean_programme(self):
		programme = self.cleaned_data['programme']
		if programme and programme.pk != Stream.objects.get(pk=self.strm).programme.pk:
			raise forms.ValidationError(_('Error. Programme field changed.'))
		return programme

	def clean_stream(self):
		stream = self.cleaned_data['stream']
		if stream and stream.pk != self.strm:
			raise forms.ValidationError(_('Error. Stream field changed.'))
		return stream
	
	def clean_photo(self):
		photo = self.cleaned_data['photo']
		if photo:
			if photo.content_type in settings.IMAGE_CONTENT_TYPE:
				if photo._size > settings.IMAGE_MAX_SIZE:
					raise forms.ValidationError(_('Image file too large (>%sMB)' % (settings.IMAGE_MAX_SIZE/(1024*1024))))
			else:
				raise forms.ValidationError(_('Please upload photo in .jpeg or .png format'))
		return photo

	def clean_resume(self):
		cv = self.cleaned_data['resume']
		if cv:
			if cv.content_type in settings.FILE_CONTENT_TYPE:
				if cv._size > settings.FILE_MAX_SIZE:
					raise forms.ValidationError(_('Resume too large (>%sMB)' % (settings.FILE_MAX_SIZE/(1024*1024))))
			else:
				raise forms.ValidationError(_('Please upload resume in .pdf, .doc or .docx format'))
		return cv
	
	def save(self, commit=True, *args, **kwargs):
		student = super(StudentCreationForm, self).save(commit=False)
		student.profile = self.user_profile
		student.is_verified = False
		if commit:
			try:
				student.save()
			except IntegrityError:
				raise forms.ValidationError(_('Couldn\'t retrieve profile'))
			except ValidationError as error:
				raise forms.ValidationError(error)
		return student
	
	class Meta:
		model = Student
		exclude = ['profile', 'is_verified', 'verified_by']
		help_texts = {
			'resume': _('Please upload resume in either pdf, doc or docx format, < %sMB' % str(settings.FILE_MAX_SIZE/(1024*1024))),
			'photo': _('Please upload image in either jpeg or png format, < %sMB' % str(settings.IMAGE_MAX_SIZE/(1024*1024))),
		}

class StudentEditForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.coll = kwargs.pop('coll', None)
		self.strm = kwargs.pop('strm', None)
		super(StudentEditForm, self).__init__(*args, **kwargs)
		self.fields['phone_number'].required = False
		self.initial['college'] = self.coll
		self.initial['stream'] = self.strm
		self.initial['programme'] = Stream.objects.get(pk=self.strm).programme.pk
		self.fields['college'].widget.attrs['disabled'] = 'disabled'
		self.fields['stream'].widget.attrs['disabled'] = 'disabled'
		self.fields['programme'].widget.attrs['disabled'] = 'disabled'

	def clean_college(self):
		college = self.cleaned_data['college']
		if college and college.pk != self.coll:
			raise forms.ValidationError(_('Error. College field changed.'))
		return college

	def clean_programme(self):
		programme = self.cleaned_data['programme']
		if programme and programme.pk != Stream.objects.get(pk=self.strm).programme.pk:
			raise forms.ValidationError(_('Error. Programme field changed.'))
		return programme

	def clean_stream(self):
		stream = self.cleaned_data['stream']
		if stream and stream.pk != self.strm:
			raise forms.ValidationError(_('Error. Stream field changed.'))
		return stream
	
	def clean_photo(self):
		photo = self.cleaned_data['photo']
		if photo:
			if photo.content_type in settings.IMAGE_CONTENT_TYPE:
				if photo._size > settings.IMAGE_MAX_SIZE:
					raise forms.ValidationError(_('Image file too large (>%sMB)' % (settings.IMAGE_MAX_SIZE/(1024*1024))))
			else:
				raise forms.ValidationError(_('Please upload photo in .jpeg or .png format'))
		return photo

	def clean_resume(self):
		cv = self.cleaned_data['resume']
		if cv:
			if cv.content_type in settings.FILE_CONTENT_TYPE:
				if cv._size > settings.FILE_MAX_SIZE:
					raise forms.ValidationError(_('Resume too large (>%sMB)' % (settings.FILE_MAX_SIZE/(1024*1024))))
			else:
				raise forms.ValidationError(_('Please upload resume in .pdf, .doc or .docx format'))
		return cv
	
	def save(self, commit=True, *args, **kwargs):
		student = super(StudentEditForm, self).save(commit=False)
		student.is_verified = kwargs.pop('verified', False)
		student.verified_by = kwargs.pop('verifier', None)
		if commit:
			try:
				student.save()
			except IntegrityError:
				raise forms.ValidationError(_('Verification error.'))
			except ValidationError as error:
				raise forms.ValidationError(error)
		return student
	
	class Meta:
		model = Student
		exclude = ['profile', 'is_verified', 'verified_by']
		help_texts = {
			'resume': _('Please upload resume in either pdf, doc or docx format, < %sMB' % str(settings.FILE_MAX_SIZE/(1024*1024))),
			'photo': _('Please upload image in either jpeg or png format, < %sMB' % str(settings.IMAGE_MAX_SIZE/(1024*1024))),
		}

class QualificationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.student_profile = kwargs.pop('student', None)
		super(QualificationForm, self).__init__(*args, **kwargs)

	def save(self, commit=True, *args, **kwargs):
		qual = super(QualificationForm, self).save(commit=False)
		qual.student = self.student_profile
		if commit:
			qual.save()
		return qual

	class Meta:
		model = Qualification
		exclude = ['student']

class QualificationEditForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(QualificationEditForm, self).__init__(*args, **kwargs)

	def save(self, commit=True, *args, **kwargs):
		qual = super(QualificationEditForm, self).save(commit=False)
		qual.is_verified = kwargs.pop('verified', None)
		qual.verified_by = kwargs.pop('verifier', None)
		if commit:
			qual.save()
		return qual

	class Meta:
		model = Qualification
		exclude = ['student']

class TechProfileForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.student_profile = kwargs.pop('student', None)
		super(TechProfileForm, self).__init__(*args, **kwargs)
	
	def clean(self, *args, **kwargs):
		super(SocialProfileForm, self).clean(*args, **kwargs)
		for field in self._meta.fields:
			if self.fields[field].__class__.__name__ == 'URLField' and self.cleaned_data[field]:
				if not field in urlparse( self.cleaned_data[field] ).netloc:
					raise forms.ValidationError({field:_('Please provide correct URL')})
	
	def save(self, commit=True, *args, **kwargs):
		tech = super(TechProfileForm, self).save(commit=False)
		tech.student = self.student_profile
		if commit:
			tech.save()
		return tech

	class Meta:
		model = TechProfile
		exclude = ['student']
