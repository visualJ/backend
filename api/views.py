from django.http import HttpResponse
import simplejson as json
import boto3
from rest_framework.decorators import api_view


# Create your views here.
def test(request):
    return HttpResponse("{\"message\":\"test\"}", content_type="application/json")


@api_view(['GET', 'PUT'])
def routes(request):
    if request.method == 'GET':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        response = table.scan(Select='ALL_ATTRIBUTES')
        json_data = json.dumps(response["Items"])
        return HttpResponse(json_data, content_type="application/json")
    elif request.method == 'PUT':
        data = request.data
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Routes')
        table.put_item(Item=data)
        response_dict = {"Success": True}
        return HttpResponse(json.dumps(response_dict), content_type="application/json")


@api_view(['GET', 'DELETE'])
def route_id(request, route_id):
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
