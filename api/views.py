from random import randint

from django.http import HttpResponse, Http404, HttpResponseBadRequest
import simplejson as json
import boto3
import hashlib
from boto3.dynamodb.conditions import Key
from math import sqrt
from rest_framework.decorators import api_view
from decimal import Decimal
import geopy.distance


def generate_id(data):
    hash_id = int(hashlib.sha1((json.dumps(data).encode())).hexdigest(), 16)
    return hash_id % 2 ** 31


# Create your views here.
def test(request):
    return HttpResponse("{\"message\":\"test\"}", content_type="application/json")


@api_view(['GET', 'POST'])
def media(request):
    s3 = boto3.client('s3')
    if request.method == 'GET':
        media_id = request.GET.get("id")
        obj = s3.get_object(Bucket="cc1-media", Key=media_id)
        body = obj["Body"].read()
        return HttpResponse(body)
    elif request.method == 'POST':
        media_file = request.data["media_file"]
        print(media_file.name)
        media_id = str(randint(0, 9223372036854775807)) + media_file.name
        s3.put_object(Bucket="cc1-media", Key=media_id, Body=media_file.read())
        response_dict = {"Success": True, "id": media_id, "Content-Type": media_file.content_type}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['GET', 'PUT'])
def routes(request):
    if request.method == 'GET':
        parameter_list = [("startCountry", "startCountry", Key.eq, str),
                          ("endCountry", "endCountry", Key.eq, str),
                          ("distance", "minDistance", Key.gte, int),
                          ("distance", "maxDistance", Key.lte, int),
                          ("duration", "minDuration", Key.gte, int),
                          ("duration", "maxDuration", Key.lte, int),
                          ("ratingAvg", "minRating", Key.gte, int),
                          ("ratingAvg", "maxRating", Key.lte, int),
                          ("difficultyAvg", "minDifficulty", Key.gte, int),
                          ("difficultyAvg", "maxDifficulty", Key.lte, int),
                          ("name", "name", Key.eq, str)]

        expression_list = []

        for db_parameter_name, parameter_name, op, type_convert in parameter_list:
            value = request.GET.get(parameter_name)
            if value is not None:
                expression_list.append(op(Key(db_parameter_name), type_convert(value)))

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        if not expression_list:
            response = table.scan(Select='ALL_ATTRIBUTES')
        else:
            expression = None
            for expression_part in expression_list:
                if expression is None:
                    expression = expression_part
                else:
                    expression &= expression_part
            response = table.scan(
                FilterExpression=expression
            )
        json_data = json.dumps(response["Items"])
        return HttpResponse(json_data, content_type="application/json")
    elif request.method == 'PUT':
        data = request.data
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        table.put_item(Item=data)
        response_dict = {"Success": True}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['POST'])
def add_poi(request):
    if request.method == 'POST':
        data = request.body
        route_id = request.GET.get('id')
        poi_data = json.loads(data)
        poi_id = generate_id(data)
        # generate new unique story_id
        poi_data["id"] = poi_id
        poi_data["location"] = [Decimal(str(poi_data["location"][0])), Decimal(str(poi_data["location"][1]))]

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')

        result = table.update_item(
            Key={
                'id': int(route_id)
            },
            UpdateExpression="SET pois = list_append(pois, :i)",
            ExpressionAttributeValues={
                ':i': [poi_data],
            },
            ReturnValues="UPDATED_NEW"
        )
        response_dict = {"id": poi_id}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['POST'])
def add_story(request):
    if request.method == 'POST':
        data = request.body
        route_id = request.GET.get('id')
        story_data = json.loads(data)
        story_id = generate_id(data)
        # generate new unique story_id
        story_data["id"] = story_id
        story_data["point"] = [Decimal(str(story_data["point"][0])), Decimal(str(story_data["point"][1]))]

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')

        result = table.update_item(
            Key={
                'id': int(route_id)
            },
            UpdateExpression="SET stories = list_append(stories, :i)",
            ExpressionAttributeValues={
                ':i': [story_data],
            },
            ReturnValues="UPDATED_NEW"
        )
        response_dict = {"id": story_id}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['POST'])
def add_rating(request):
    if request.method == 'POST':
        data = request.body
        route_id = request.GET.get('id')
        ratings_data = json.loads(data)
        # generate new unique ratings_id
        ratings_id = generate_id(data)
        ratings_data["id"] = ratings_id

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')

        result = table.update_item(
            Key={
                'id': int(route_id)
            },
            UpdateExpression="SET ratings = list_append(ratings, :i)",
            ExpressionAttributeValues={
                ':i': [ratings_data],
            },
            ReturnValues="UPDATED_NEW"
        )
        response_dict = {"id": ratings_id}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['GET', 'DELETE'])
def route_by_id(request, route_id):
    if request.method == 'GET':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        response = table.get_item(
            Key={
                'id': int(route_id)
            }
        )
        item = response["Item"]
        return HttpResponse(json.dumps(item), content_type="application/json")
    elif request.method == 'DELETE':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        table.delete_item(
            Key={
                'id': int(route_id)
            }
        )
        response_dict = {"Success": True}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['GET'])
def route_detail(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Routes')
    if 'id' not in request.GET:
        return HttpResponseBadRequest("Missing id query parameter")
    route_id = request.GET.get('id')
    response = table.get_item(
        Key={
            'id': int(route_id)
        }
    )
    if 'Item' not in response:
        raise Http404()
    item = response["Item"]
    return HttpResponse(json.dumps(item), content_type="application/json")


@api_view(['GET'])
def check_sponsoring(request):
    route_id = request.query_params.get('id')
    x1 = request.query_params.get('x1')
    x2 = request.query_params.get('x2')
    y1 = request.query_params.get('y1')
    y2 = request.query_params.get('y2')
    p1 = (Decimal(x1), Decimal(y1))
    p2 = (Decimal(x2), Decimal(y2))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Routes')
    route_data = table.get_item(
        Key={
            'id': int(route_id)
        }
    )["Item"]
    print(route_data.keys())
    route_points = route_data["points"]
    start_end_point = None
    last_point = None
    distance = 0
    for (px, py) in route_points:
        if start_end_point:
            if last_point:
                distance += geopy.distance.vincenty(last_point, (px, py)).km
            last_point = (px, py)
        else:
            if p1 == (px, py):
                start_end_point = (p1, p2)
            if p2 == (px, py):
                start_end_point = (p2, p1)
    price = distance * float(route_data["sponsorPricePerKm"])
    response_dict = {
        "distance": distance,
        "price": price,
        "start_point": start_end_point[0],
        "end_point": start_end_point[1]
    }
    return HttpResponse(json.dumps(response_dict), content_type="application/json")
