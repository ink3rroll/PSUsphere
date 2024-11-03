class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            # Add more fields as necessary
        }