# Generated by Django 4.2.10 on 2024-03-11 09:57

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
                (
                    "tx_hash",
                    gnosis.eth.django.models.Keccak256Field(
                        primary_key=True, serialize=False
                    ),
                ),
                ("block_hash", gnosis.eth.django.models.Keccak256Field()),
                ("block_number", gnosis.eth.django.models.Uint32Field()),
                ("block_timestamp", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="StatusEventsIndexer",
            fields=[
                (
                    "contract",
                    gnosis.eth.django.models.EthereumAddressV2Field(
                        primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("deployed_block", models.PositiveIntegerField()),
                ("last_indexed_block", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="WithdrawnEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("timestamp", models.DateTimeField()),
                ("log_index", gnosis.eth.django.models.Uint32Field()),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", gnosis.eth.django.models.Uint96Field()),
                ("unlock_index", gnosis.eth.django.models.Uint32Field()),
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
            name="UnlockEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("timestamp", models.DateTimeField()),
                ("log_index", gnosis.eth.django.models.Uint32Field()),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", gnosis.eth.django.models.Uint96Field()),
                ("unlock_index", gnosis.eth.django.models.Uint32Field()),
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
            name="LockEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("timestamp", models.DateTimeField()),
                ("log_index", gnosis.eth.django.models.Uint32Field()),
                ("holder", gnosis.eth.django.models.EthereumAddressV2Field()),
                ("amount", gnosis.eth.django.models.Uint96Field()),
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
        migrations.AddConstraint(
            model_name="lockevent",
            constraint=models.UniqueConstraint(
                fields=("ethereum_tx", "log_index"), name="unique_ethereum_tx_log_index"
            ),
        ),
    ]
