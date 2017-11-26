from django.http import HttpResponse
import simplejson as json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from rest_framework.decorators import api_view


# Create your views here.
def test(request):
    return HttpResponse("{\"message\":\"test\"}", content_type="application/json")


@api_view(['GET', 'PUT'])
def routes(request):
    if request.method == 'GET':
        parameter_list = [("startCountry", "startCountry", "eg", str),
                          ("endCountry", "endCountry", "eg", str),
                          ("distance", "minDistance", "gt", int),
                          ("distance", "maxDistance", "lt", int),
                          ("duration", "minDuration", "gt", int),
                          ("duration", "maxDuration", "lt", int),
                          ("ratingAvg", "minRating", "gte", int),
                          ("ratingAvg", "maxRating", "lte", int),
                          ("name", "name", "eg", str)]

        operator_dict = {"eg": lambda parameter_name, parameter_value: Key(parameter_name).eq(parameter_value),
                         "lt": lambda parameter_name, parameter_value: Key(parameter_name).lt(parameter_value),
                         "gt": lambda parameter_name, parameter_value: Key(parameter_name).gt(parameter_value),
                         "lte": lambda parameter_name, parameter_value: Key(parameter_name).lte(parameter_value),
                         "gte": lambda parameter_name, parameter_value: Key(parameter_name).gte(parameter_value)}
        expression_list = []

        for db_parameter_name, parameter_name, op, type_convert in parameter_list:
            value = request.GET.get(parameter_name)
            if value is not None:
                expression_list.append(operator_dict[op](db_parameter_name, type_convert(value)))

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
