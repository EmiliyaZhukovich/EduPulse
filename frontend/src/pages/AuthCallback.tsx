import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const redirect = searchParams.get('redirect') || '/';

    setTimeout(() => {
      navigate(redirect);
    }, 1000);
  }, [navigate, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">Authenticating...</h2>
        <p className="text-gray-600">Please wait while we complete your login.</p>
      </div>
    </div>
  );
};

export default AuthCallback;
