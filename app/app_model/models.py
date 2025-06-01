
import os
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from uuid import uuid4

# Create your models here.

class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    user_category = models.CharField(max_length=50, default='pending', null=True, blank=True)
    user_role = models.CharField(max_length=100, default='pending', null=True, blank=True)
    user_status = models.CharField(max_length=50, default='pending', null=True, blank=True)
    # FK --
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='details')

    def __str__(self) -> str:
        return self.user_name

    class Meta:
        db_table = 'auth_user_details'
        

def map_files_path(instance, filename):
    unique_id = uuid.uuid4().hex[:10]
    extension = filename.split('.')[-1]
    new_filename = f"{unique_id}.{extension}"

    return os.path.join('map_files', new_filename)

class MapShapeFile(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.CharField(max_length=100, blank=True, null=True)
    category_name = models.CharField(max_length=250, null=True, blank=True)
    file_path = models.FileField(upload_to=map_files_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    entry_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self) -> str:
        return self.category_id

    class Meta:
        db_table = 'tbl_map_files'
        

class MapLegend(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.CharField(max_length=50, null=False, blank=False)
    category_name = models.CharField(max_length=200, null=True, blank=True)
    display_header = models.CharField(max_length=200, null=True, blank=True)
    legend_color = models.CharField(max_length=200, null=True, blank=True)
    legend_value = models.CharField(max_length=256, null=True, blank=True)
    sorting =  models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    watershed_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.legend_value or ''

    class Meta:
        db_table = 'tbl_map_legend'


class Division(models.Model):
    div_geo_code = models.CharField(max_length=2)
    div_name = models.CharField(primary_key=True, max_length=100)
    div_name_bng = models.CharField(max_length=200)
    sorting_order = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.div_name

    class Meta:
        db_table = 'lkp_division'
        ordering = ['div_name']


class District(models.Model):
    dist_geo_code = models.CharField(max_length=4)
    dist_name = models.CharField(primary_key=True, max_length=100)
    dist_name_bng = models.CharField(max_length=200)
    sorting_order = models.PositiveSmallIntegerField(null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.PROTECT, null=True)

    def __str__(self) -> str:
        return self.dist_name

    class Meta:
        db_table = 'lkp_district'
        ordering = ['dist_name']
        

class Watershed(models.Model):
    watershed_code = models.CharField(primary_key=True, max_length=8)
    watershed_name = models.CharField(max_length=200)
    watershed_name_bng = models.CharField( max_length=200, blank=True)
    serial = models.PositiveSmallIntegerField(null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, null=True, db_column='district_name')

    def __str__(self) -> str:
        return self.watershed_name

    class Meta:
        db_table = 'lkp_watershed'
        ordering = ['watershed_code']
        

class ParaMapLegend(models.Model):
    id = models.AutoField(primary_key=True)
    watershed_id = models.CharField(max_length=100)
    legend_title = models.CharField(max_length=100, blank=True, null=True)
    para_name = models.CharField(max_length=100, blank=True, null=True)
    legend_color = models.CharField(max_length=50, blank=True, null=True)
    entry_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    sorting = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.watershed_id

    class Meta:
        db_table = 'tbl_para_map_legend'
        

class LayerMapColor(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.CharField(max_length=50, null=False, blank=False)
    category_name = models.CharField(max_length=200, null=True, blank=True)
    watershed = models.ForeignKey(Watershed, on_delete=models.PROTECT, null=True, verbose_name='watershed Name')
    para_name = models.CharField(max_length=200, null=True, blank=True)
    actual_value = models.CharField(max_length=200, null=True, blank=True)
    legend_value = models.CharField(max_length=256, null=True, blank=True)
    layer_color = models.CharField(max_length=200, null=True, blank=True)
    sorting =  models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.category_name or ''

    class Meta:
        db_table = 'tbl_layer_map_color'


class ParaWiseLayerInfo(models.Model):
    id = models.AutoField('Id', primary_key=True)
    category_id = models.CharField('Category Id', max_length=200)
    category_name = models.CharField('Category Name', max_length=256, blank=True)
    para_name = models.CharField('Para Name', max_length=256, blank=True)
    description = models.CharField('Description', max_length=256, blank=True)
    chakma = models.CharField('chakma', max_length=100, blank=True, null=True)
    marma = models.CharField('marma', max_length=100, blank=True, null=True)
    tripura = models.CharField('tripura', max_length=100, blank=True, null=True)
    cmnt_mro = models.CharField('mro', max_length=100, blank=True, null=True)
    tanchangya = models.CharField('tanchangya', max_length=100, blank=True, null=True)
    bawm = models.CharField('bawm', max_length=100, blank=True, null=True)
    chak = models.CharField('chak', max_length=100, blank=True, null=True)
    khyang = models.CharField('khyang', max_length=100, blank=True, null=True)
    khumi = models.CharField('khumi', max_length=100, blank=True, null=True)
    lushai = models.CharField('lushai', max_length=100, blank=True, null=True)
    pankhua = models.CharField('pankhua', max_length=100, blank=True, null=True)
    non_ips = models.CharField('non_ips', max_length=100, blank=True, null=True)
    manipuri = models.CharField(max_length=100, blank=True, null=True)
    total = models.CharField('Total', max_length=100, blank=True, null=True)
    sorting =  models.PositiveSmallIntegerField('Order', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.para_name

    class Meta:
        verbose_name_plural = "Para Wise Layer Info"
        db_table = 'tbl_para_wise_layer_info_new'
 
 
class ParaWiseEducationInfo(models.Model):
    id = models.AutoField(primary_key=True)
    para_name = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=256, blank=True)
    institution_number = models.CharField(max_length=100, blank=True, null=True)
    average_distance = models.CharField(max_length=100, blank=True, null=True)
    average_time = models.CharField(max_length=100, blank=True, null=True)
    sorting =  models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.para_name

    class Meta:
        db_table = 'tbl_education_info'
        ordering = ['sorting']


class ParaWiseLiteracyInfo(models.Model):
    id = models.AutoField(primary_key=True)
    para_name = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=256, blank=True)
    male = models.CharField(max_length=100, blank=True, null=True)
    female = models.CharField(max_length=100, blank=True, null=True)
    total = models.CharField(max_length=100, blank=True, null=True)
    sorting =  models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.para_name

    class Meta:
        db_table = 'tbl_literacy_info'
        ordering = ['sorting']


class OneValueBasedTabular(models.Model):
    id = models.AutoField('Id', primary_key=True)
    category_id = models.CharField('Para Name', max_length=256, blank=True)
    category_name = models.CharField('Para Name', max_length=256, blank=True)
    para_name = models.CharField('Para Name', max_length=256, blank=True)
    description = models.CharField('Description', max_length=256, blank=True)
    value = models.CharField('Exposure', max_length=100, blank=True, null=True)
    sorting =  models.PositiveSmallIntegerField('Order', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.para_name

    class Meta:
        db_table = 'tbl_one_value_tabular_data'
        

class Units(models.Model):
    id = models.AutoField(primary_key=True)
    unit_name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.unit_name

    class Meta:
        db_table = 'lkp_unit'
        ordering = ['-created_at']


class Components(models.Model):
    id = models.AutoField(primary_key=True)
    component_name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.component_name

    class Meta:
        db_table = 'lkp_component'
        ordering = ['-created_at']        


class Indicators(models.Model):
    id = models.AutoField(primary_key=True)
    indicator_name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # FK --
    component = models.OneToOneField('Components', on_delete=models.CASCADE, null=True, blank=True, related_name='indicator')

    def __str__(self) -> str:
        return self.indicator_name

    class Meta:
        db_table = 'lkp_indicator'
        ordering = ['-created_at'] 


class Parameters(models.Model):
    id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # FK --
    indicator = models.OneToOneField('Indicators', on_delete=models.CASCADE, null=True, blank=True, related_name='parameter')

    def __str__(self) -> str:
        return self.parameter_name or f"Parameter {self.id}"

    class Meta:
        db_table = 'lkp_parameter'
        ordering = ['-created_at']
         

class WatershedHealth(models.Model):
    id = models.AutoField(primary_key=True)
    baseline_2024 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2030 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2035 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2041 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2050 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_special = models.BooleanField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # FK --
    watershed = models.OneToOneField('Watershed', on_delete=models.CASCADE, null=True, blank=True, related_name='watershed_health')
    parameter = models.OneToOneField('Parameters', on_delete=models.CASCADE, null=True, blank=True, related_name='watershed_health')

    def __str__(self) -> str:
        return f"Watershed Health {self.id} - Baseline: {self.baseline_2024}"

    class Meta:
        db_table = 'tbl_watershed_health'
        ordering = ['-created_at']        
        

class ClimateResilience(models.Model):
    id = models.AutoField(primary_key=True)
    baseline_2024 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2030 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2035 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2041 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2050 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_special = models.BooleanField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # FK --
    watershed = models.OneToOneField('Watershed', on_delete=models.CASCADE, null=True, blank=True, related_name='climate_resilience')
    parameter = models.OneToOneField('Parameters', on_delete=models.CASCADE, null=True, blank=True, related_name='climate_resilience')

    def __str__(self) -> str:
        return self.baseline_2024

    class Meta:
        db_table = 'tbl_climate_resilience'
        ordering = ['-created_at']



