routes = {
    "/": {
        "type": "static",
        "file": "index.html",
        "methods": ["get"]
    },

    "/api/get_base_info": {
        "type": "dynamic",
        "file": "get_base_info",
        "methods": ["post"]
    },

    "/api/get_profile_pictures": {
        "type": "dynamic",
        "file": "get_profile_pictures",
        "methods": ["post"]
    },

    "/api/get_generals": {
        "type": "dynamic",
        "file": "get_generals",
        "methods": ["post"]
    },

    "/api/get_charts_all_time": {
        "type": "dynamic",
        "file": "get_charts_all_time",
        "methods": ["post"]
    },

    "/api/get_charts_time": {
        "type": "dynamic",
        "file": "get_charts_time",
        "methods": ["post"]
    },

    "/api/get_charts_media": {
        "type": "dynamic",
        "file": "get_charts_media",
        "methods": ["post"]
    },

    "/api/get_chats": {
        "type": "dynamic",
        "file": "get_chats",
        "methods": ["post"]
    },

    "/api/get_misc": {
        "type": "dynamic",
        "file": "get_misc",
        "methods": ["post"]
    },

    "/api/get_text": {
        "type": "dynamic",
        "file": "get_text",
        "methods": ["post"]
    }
}