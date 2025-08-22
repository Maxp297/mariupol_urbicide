import pytest
from scripts.generate_address_variants import \
    generate_variants_ru, generate_variants_uk, generate_variants_en

def test_generate_variants_ru():
    street = "Морской"
    number = "46"

    expected_variants = [
        f'{number}', f'{number} к.1', f'{number} корп.1', f'{number}-1', f'{number}-ий', f'{number}-й', f'{number}/1',
        f'{number}A', f'{number}a', f'{number}А', f'{number}а',
        f'{street} {number}', f'{street} б-р {number}', f'{street} б-р д. {number}', f'{street} б-р д.{number}',
        f'{street} б-р дом {number}', f'{street} б-р №{number}', f'{street} б-р, {number}', f'{street} б-р, д. {number}',
        f'{street} б-р, д.{number}', f'{street} б-р, дом {number}', f'{street} б-р, №{number}', f'{street} бул. {number}',
        f'{street} бул. д. {number}', f'{street} бул. д.{number}', f'{street} бул. дом {number}', f'{street} бул. №{number}',
        f'{street} бул., {number}', f'{street} бул., д. {number}', f'{street} бул., д.{number}', f'{street} бул., дом {number}',
        f'{street} бул., №{number}', f'{street} бульвар {number}', f'{street} бульвар д. {number}', f'{street} бульвар д.{number}',
        f'{street} бульвар дом {number}', f'{street} бульвар №{number}', f'{street} бульвар, {number}', f'{street} бульвар, д. {number}',
        f'{street} бульвар, д.{number}', f'{street} бульвар, дом {number}', f'{street} бульвар, №{number}', f'{street} д. {number}',
        f'{street} д.{number}', f'{street} дом {number}', f'{street} №{number}', f'{street}, {number}', f'{street}, д. {number}',
        f'{street}, д.{number}', f'{street}, дом {number}', f'{street}, №{number}', f'б-р {street} {number}', f'б-р {street} д. {number}',
        f'б-р {street} д.{number}', f'б-р {street} дом {number}', f'б-р {street} №{number}', f'б-р {street}, {number}',
        f'б-р {street}, д. {number}', f'б-р {street}, д.{number}', f'б-р {street}, дом {number}', f'б-р {street}, №{number}',
        f'бул. {street} {number}', f'бул. {street} д. {number}', f'бул. {street} д.{number}', f'бул. {street} дом {number}',
        f'бул. {street} №{number}', f'бул. {street}, {number}', f'бул. {street}, д. {number}', f'бул. {street}, д.{number}',
        f'бул. {street}, дом {number}', f'бул. {street}, №{number}', f'бульвар {street} {number}', f'бульвар {street} д. {number}',
        f'бульвар {street} д.{number}', f'бульвар {street} дом {number}', f'бульвар {street} №{number}', f'бульвар {street}, {number}',
        f'бульвар {street}, д. {number}', f'бульвар {street}, д.{number}', f'бульвар {street}, дом {number}', f'бульвар {street}, №{number}',
        f'д. {number}', f'д.{number}', f'дом {number}', f'№{number}'
    ]

    variants = generate_variants_ru(street, number)

    # Check exact match
    assert sorted(variants) == sorted(expected_variants)


def test_generate_variants_uk():
    street = "Морський"
    number = "46"

    expected_variants = [
        f'{number}', f'{number} к.1', f'{number} корп.1', f'{number}-1', f'{number}-ий', f'{number}-й', f'{number}/1',
        f'{number}A', f'{number}a', f'{number}А', f'{number}а',
        f'{street} {number}', f'{street} б-р {number}', f'{street} б-р буд. {number}', f'{street} б-р буд.{number}',
        f'{street} б-р будинок {number}', f'{street} б-р №{number}', f'{street} б-р, {number}', f'{street} б-р, буд. {number}',
        f'{street} б-р, буд.{number}', f'{street} б-р, будинок {number}', f'{street} б-р, №{number}', f'{street} бул. {number}',
        f'{street} бул. буд. {number}', f'{street} бул. буд.{number}', f'{street} бул. будинок {number}', f'{street} бул. №{number}',
        f'{street} бул., {number}', f'{street} бул., буд. {number}', f'{street} бул., буд.{number}', f'{street} бул., будинок {number}',
        f'{street} бул., №{number}', f'{street} бульвар {number}', f'{street} бульвар буд. {number}', f'{street} бульвар буд.{number}',
        f'{street} бульвар будинок {number}', f'{street} бульвар №{number}', f'{street} бульвар, {number}', f'{street} бульвар, буд. {number}',
        f'{street} бульвар, буд.{number}', f'{street} бульвар, будинок {number}', f'{street} бульвар, №{number}', f'{street} буд. {number}',
        f'{street} буд.{number}', f'{street} будинок {number}', f'{street} №{number}', f'{street}, {number}', f'{street}, буд. {number}',
        f'{street}, буд.{number}', f'{street}, будинок {number}', f'{street}, №{number}', f'б-р {street} {number}', f'б-р {street} буд. {number}',
        f'б-р {street} буд.{number}', f'б-р {street} будинок {number}', f'б-р {street} №{number}', f'б-р {street}, {number}',
        f'б-р {street}, буд. {number}', f'б-р {street}, буд.{number}', f'б-р {street}, будинок {number}', f'б-р {street}, №{number}',
        f'бул. {street} {number}', f'бул. {street} буд. {number}', f'бул. {street} буд.{number}', f'бул. {street} будинок {number}',
        f'бул. {street} №{number}', f'бул. {street}, {number}', f'бул. {street}, буд. {number}', f'бул. {street}, буд.{number}',
        f'бул. {street}, будинок {number}', f'бул. {street}, №{number}', f'бульвар {street} {number}', f'бульвар {street} буд. {number}',
        f'бульвар {street} буд.{number}', f'бульвар {street} будинок {number}', f'бульвар {street} №{number}', f'бульвар {street}, {number}',
        f'бульвар {street}, буд. {number}', f'бульвар {street}, буд.{number}', f'бульвар {street}, будинок {number}', f'бульвар {street}, №{number}',
        f'буд. {number}', f'буд.{number}', f'будинок {number}', f'№{number}'
    ]

    variants = generate_variants_uk(street, number)

    # Check exact match
    assert sorted(variants) == sorted(expected_variants)


def test_generate_variants_en():
    street = "Morsky"
    number = "46"

    expected_variants = [
        f'{number}', f'{number} Blvd. {street}', f'{number} Blvd. {street}', f'{number} Blvd. {street}.', f'{number} {street}',
        f'{number} {street}', f'{number} {street} Blvd.', f'{number} {street} Blvd.', f'{number} {street} Blvd..',
        f'{number} {street} Boulevard', f'{number} {street} Boulevard', f'{number} {street} Boulevard.',
        f'{number} {street} blvd', f'{number} {street} blvd', f'{number} {street} blvd.', f'{number} {street}.',
        f'{number} bldg 1', f'{number} corp 1', f'{number}-1', f'{number}/1', f'{number}A', f'{number}a', f'{number}th',
        f'Blvd. {street} #{number}', f'Blvd. {street} {number}', f'Blvd. {street} {number}', f'Blvd. {street} Building {number}',
        f'Blvd. {street} No. {number}', f'Blvd. {street}, {number}', f'Building {number}', f'{street} #{number}', f'{street} {number}',
        f'{street} {number}', f'{street} Blvd. #{number}', f'{street} Blvd. {number}', f'{street} Blvd. {number}',
        f'{street} Blvd. Building {number}', f'{street} Blvd. No. {number}', f'{street} Blvd., {number}',
        f'{street} Boulevard #{number}', f'{street} Boulevard {number}', f'{street} Boulevard {number}',
        f'{street} Boulevard Building {number}', f'{street} Boulevard No. {number}',
        f'{street} Boulevard, {number}', f'{street} Building {number}', f'{street} No. {number}',
        f'{street} blvd #{number}', f'{street} blvd {number}', f'{street} blvd {number}',
        f'{street} blvd Building {number}', f'{street} blvd No. {number}', f'{street} blvd, {number}',
        f'{street}, {number}', f'No. {number}'
    ]

    variants = generate_variants_en(street, number)

    # Check exact match
    assert sorted(variants) == sorted(expected_variants)
