from app.api import bp

@bp.route('/raids/<string:discord_id>', methods=['PUT'])
def get_raid(discord_id):
    pass

@bp.route('raids', methods=['GET'])
def get_raids():
    pass

""" @bp.route('/raids', methods=['POST'])
def post_raid():
    pass
 """
@bp.route('/raids/<string:discord_id>', methods=['PUT'])
def update_raid(discord_id):
    pass