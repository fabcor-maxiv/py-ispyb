from flask_restplus import Namespace, Resource
from ispyb import app
#from ispyb.models import Proposal
#from ispyb.schemas import ProposalSchema
from ispyb.auth import token_required

#proposals_schema = ProposalSchema(many=True)
ns = Namespace('Data collection group', description='Data collection group related namespace', path='dcgr')

@ns.route("/list")
class DataCollectionGroupList(Resource):
    """Data collection group resource"""

    @ns.doc(security="apikey")
    #@token_required
    def get(self):
        """Returns all data collection groups"""
        return 'TODO'
        #app.logger.info('')
        #proposals = Proposal.query.all()
        #return proposals_schema.dump(proposals)
