from django.http import HttpResponse
import simplejson as json
import boto3


# Create your views here.
def test(request):
    return HttpResponse("{\"message\":\"test\"}", content_type="application/json")


def routes(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Routes')
    response = table.scan(Select='ALL_ATTRIBUTES')
    json_data = json.dumps(response["Items"])
    return HttpResponse(json_data, content_type="application/json")