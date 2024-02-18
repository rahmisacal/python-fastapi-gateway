#UserRole

    $oc adm policy add-cluster-role-to-user cluster-admin -z sa-cluster-admin --rolebinding-name=cloud-admins -n default
    $oc sa get-token sa-cluster-admin

#Ovirt and Openshift ApiGateway
    
    This is a basic gateway where front of ovirt and openshift engine. 
    Include basic authentication, calls limit with period, json output structure and include only get request.
    If you face any security or other issues, you can detect it at this apigateway and catch it and you can cut the connectivity with the back side(engine api's) at this layer 
