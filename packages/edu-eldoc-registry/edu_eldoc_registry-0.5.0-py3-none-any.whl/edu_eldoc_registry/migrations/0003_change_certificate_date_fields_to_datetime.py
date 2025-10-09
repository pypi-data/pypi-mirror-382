from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    dependencies = [
        ('edu_eldoc_registry', '0002_alter_document_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='date_from',
            field=models.DateTimeField(
                verbose_name='Действителен с'
            ),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='date_to',
            field=models.DateTimeField(
                verbose_name='Действителен до'
            ),
        ),
    ]
