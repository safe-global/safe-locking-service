# Generated by Django 4.2.10 on 2024-02-27 10:44

import django.db.models.deletion
from django.db import migrations, models

import gnosis.eth.django.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EthereumTx",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "tx_hash",
                    gnosis.eth.django.models.Keccak256Field(
                        primary_key=True, serialize=False
                    ),
                ),
                ("block_hash", gnosis.eth.django.models.Keccak256Field()),
                ("block_number", models.PositiveIntegerField()),
                ("block_timestamp", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="UnlockEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", models.PositiveIntegerField()),
                ("log_index", models.PositiveIntegerField()),
                ("block_timestamp", models.DateTimeField()),
                ("unlock_index", models.PositiveIntegerField()),
                (
                    "ethereum_tx",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="locking_events.ethereumtx",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WithdrawnEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", models.PositiveIntegerField()),
                ("log_index", models.PositiveIntegerField()),
                ("block_timestamp", models.DateTimeField()),
                (
                    "ethereum_tx",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="locking_events.ethereumtx",
                    ),
                ),
                (
                    "unlock_index",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="locking_events.unlockevent",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LockEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", models.PositiveIntegerField()),
                ("log_index", models.PositiveIntegerField()),
                ("block_timestamp", models.DateTimeField()),
                (
                    "ethereum_tx",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="locking_events.ethereumtx",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="withdrawnevent",
            constraint=models.UniqueConstraint(
                fields=("holder", "unlock_index"), name="unique_withdrawn_event_index"
            ),
        ),
        migrations.AddConstraint(
            model_name="unlockevent",
            constraint=models.UniqueConstraint(
                fields=("holder", "unlock_index"), name="unique_unlock_event_index"
            ),
        ),
    ]
