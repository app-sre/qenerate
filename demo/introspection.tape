Output introspection.gif

Set FontSize 20
Set Width 1600
Set Height 600

Type "# 1. Make sure you have a reachable GraphQL server backend"
Sleep 1s
Enter

Type "curl localhost:4000/graphql"
Sleep 1s
Enter
Enter
Sleep 2s

Hide
Type "clear"
Enter
Show

Type "# 2. Make an introspection query to the GraphQL server"
Sleep 1s
Enter

Type "qenerate introspection http://localhost:4000/graphql > gql/introspection.json"
Sleep 1s
Enter
Sleep 1s
Type "cat gql/introspection.json"
Enter
Sleep 2s

Type "# The introspection.json will be used during code generation to properly infer types"
Sleep 1s
Enter
Sleep 2s
