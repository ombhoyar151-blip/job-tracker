from api.routes.auth import router as auth_router
from api.routes.profile import router as profile_router
from api.routes.resumes import router as resumes_router
from api.routes.jobs import router as jobs_router
from api.routes.dashboard import router as dashboard_router
from api.routes.applications import router as applications_router
from api.routes.interviews import router as interviews_router
from api.routes.notifications import router as notifications_router
from api.routes.insights import router as insights_router

routers = [auth_router, profile_router, resumes_router, jobs_router, dashboard_router, applications_router, interviews_router, notifications_router, insights_router]
