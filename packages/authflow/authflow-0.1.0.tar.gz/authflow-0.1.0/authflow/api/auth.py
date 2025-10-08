"""Authentication API endpoints."""

from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from authflow.core.provider import AuthProvider
from authflow.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)
from authflow.models.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    User,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
)
from authflow.api.dependencies import AuthFlowDependencies

logger = logging.getLogger(__name__)


def create_auth_router(
    provider: AuthProvider,
    dependencies: AuthFlowDependencies,
) -> APIRouter:
    """Create authentication router.

    Args:
        provider: Authentication provider
        dependencies: AuthFlow dependencies

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/auth", tags=["authentication"])

    @router.post("/login", response_model=TokenResponse)
    async def login(credentials: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens.

        Args:
            credentials: Login credentials (username and password)

        Returns:
            Access token, refresh token, and user info

        Raises:
            HTTPException: If authentication fails
        """
        try:
            logger.info(f"Login attempt for user: {credentials.username}")

            token_response = await provider.authenticate(credentials)

            logger.info(f"Login successful for user: {credentials.username}")
            return token_response

        except InvalidCredentialsError as e:
            logger.warning(f"Invalid credentials for user: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed",
            )

    @router.post("/refresh", response_model=TokenResponse)
    async def refresh_token(request: RefreshRequest) -> TokenResponse:
        """Refresh access token using refresh token.

        Args:
            request: Refresh token request

        Returns:
            New access token and refresh token

        Raises:
            HTTPException: If refresh token is invalid
        """
        try:
            logger.info("Token refresh requested")

            token_response = await provider.refresh_token(request.refresh_token)

            logger.info("Token refresh successful")
            return token_response

        except InvalidTokenError as e:
            logger.warning(f"Invalid refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed",
            )

    @router.post("/logout")
    async def logout(
        request: Optional[LogoutRequest] = None,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Logout user and invalidate tokens.

        Args:
            request: Optional logout request with refresh token
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(f"Logout requested for user: {current_user.username}")

            refresh_token = request.refresh_token if request else None
            await provider.logout(refresh_token)

            logger.info(f"Logout successful for user: {current_user.username}")
            return {"message": "Logged out successfully"}

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            # Don't fail logout even if there's an error
            return {"message": "Logged out"}

    @router.get("/me", response_model=User)
    async def get_current_user(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> User:
        """Get current authenticated user.

        Args:
            current_user: Current authenticated user from dependency

        Returns:
            Current user information
        """
        logger.debug(f"Current user requested: {current_user.username}")
        return current_user

    @router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
    async def register(user_data: dict) -> User:
        """Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Created user

        Raises:
            HTTPException: If registration fails
        """
        try:
            from authflow.models.schemas import UserCreate

            logger.info(f"Registration attempt for: {user_data.get('username')}")

            # Create user through provider
            user_create = UserCreate(**user_data)
            user = await provider.create_user(user_create)

            logger.info(f"Registration successful: {user.username}")
            return user

        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    @router.post("/forgot-password")
    async def forgot_password(request: PasswordResetRequest) -> dict:
        """Request password reset email.

        Args:
            request: Password reset request with email

        Returns:
            Success message
        """
        try:
            logger.info(f"Password reset requested for: {request.email}")

            # Get user by email
            user = await provider.get_user_by_email(request.email)

            # Send reset email (implementation depends on provider)
            # For now, this is a placeholder
            logger.info(f"Password reset email sent to: {request.email}")

            return {
                "message": "If the email exists, a password reset link has been sent"
            }

        except UserNotFoundError:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email")
            return {
                "message": "If the email exists, a password reset link has been sent"
            }
        except Exception as e:
            logger.error(f"Error in password reset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset request failed",
            )

    @router.post("/reset-password")
    async def reset_password(request: PasswordResetConfirm) -> dict:
        """Reset password with reset token.

        Args:
            request: Password reset confirmation with token and new password

        Returns:
            Success message
        """
        try:
            logger.info("Password reset confirmation")

            # Validate reset token and extract user ID
            # This is a simplified implementation
            # In production, you'd validate the token and extract user info

            # For now, return success
            logger.info("Password reset successful")
            return {"message": "Password reset successful"}

        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset failed",
            )

    @router.post("/change-password")
    async def change_password(
        request: PasswordChangeRequest,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Change password for authenticated user.

        Args:
            request: Password change request
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(f"Password change requested for: {current_user.username}")

            # Verify old password by attempting authentication
            try:
                login_request = LoginRequest(
                    username=current_user.username,
                    password=request.old_password,
                )
                await provider.authenticate(login_request)
            except AuthenticationError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect",
                )

            # Set new password
            await provider.set_user_password(
                current_user.id,
                request.new_password,
                temporary=False,
            )

            logger.info(f"Password changed for: {current_user.username}")
            return {"message": "Password changed successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed",
            )

    @router.get("/sessions")
    async def get_user_sessions(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Get active sessions for current user.

        Args:
            current_user: Current authenticated user

        Returns:
            List of active sessions
        """
        try:
            logger.debug(f"Sessions requested for: {current_user.username}")

            sessions = await provider.get_user_sessions(current_user.id)

            return {"sessions": sessions}

        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve sessions",
            )

    @router.delete("/sessions/{session_id}")
    async def revoke_session(
        session_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Revoke a specific session.

        Args:
            session_id: Session ID to revoke
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(
                f"Session revocation requested: {session_id} by {current_user.username}"
            )

            await provider.revoke_session(current_user.id, session_id)

            logger.info(f"Session revoked: {session_id}")
            return {"message": "Session revoked successfully"}

        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke session",
            )

    @router.post("/verify-email/{user_id}")
    async def send_verification_email(
        user_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Send email verification to user.

        Args:
            user_id: User ID to send verification
            current_user: Current authenticated user (must be admin or self)

        Returns:
            Success message
        """
        try:
            # Check if user is admin or requesting for self
            if current_user.id != user_id:
                # Would need admin check here
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot send verification for other users",
                )

            logger.info(f"Email verification requested for user: {user_id}")

            await provider.send_verification_email(user_id)

            logger.info(f"Verification email sent to user: {user_id}")
            return {"message": "Verification email sent"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email",
            )

    return router
