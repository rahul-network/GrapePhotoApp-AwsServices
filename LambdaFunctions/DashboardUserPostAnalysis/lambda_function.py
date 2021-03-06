# DashboardService: calculate the user posts statistics

from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr
import json
import boto3
import decimal
import uuid
from resultFormatter import getResultSingle, getResultMultiple, getResultError

dynamodb_resource = resource('dynamodb')

def lambda_handler(event, context):
    projection_exp='UserId, LikeCount'
    data = get_items("Post",projection_exp)
    items=data['Items']
    result = {}
    for item in items:
        # create user
        if not result.has_key(item["UserId"]):
            result[item["UserId"]]={}
            result[item["UserId"]]["UserId"]=item["UserId"]
            result[item["UserId"]]["Rank"]=0

        # Update the post count
        if not result[item["UserId"]].has_key("Posts"):
            result[item["UserId"]]["Posts"]=1
        else:
            result[item["UserId"]]["Posts"]+=1

    # caculate the rank of each user
    index = 1
    for key, value in sorted(result.iteritems(), key=lambda (k,v): (-v["Posts"],k)):
        value["Rank"]=index
        index+=1

    # save the ranked records to database
    for record in result.values():
        put_item("User_Post_Rank_Analysis", record)
    return result

def get_items(table_name, projExpr):
    table = dynamodb_resource.Table(table_name)
    data = table.scan(ProjectionExpression=projExpr)
    return data

def put_item(table_name, item):
    table = dynamodb_resource.Table(table_name)
    table.put_item(Item=item)
    return
