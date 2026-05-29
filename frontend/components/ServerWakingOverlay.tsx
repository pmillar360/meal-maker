import { FaCheck } from 'react-icons/fa';
import { useServerStatus } from '../context/ServerStatusContext';

export default function ServerWakingOverlay() {
  const { serverStatus } = useServerStatus();

  if (serverStatus === 'awake') return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-sm w-full mx-4 text-center">
        {serverStatus === 'asleep' ? (
          <>
            <div className="w-14 h-14 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-5" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Server is Waking Up</h2>
            <p className="text-gray-500 text-sm leading-relaxed">
              The server is starting up from sleep. This can take up to 30 seconds on the free tier — hang tight!
            </p>
          </>
        ) : (
          <>
            <div className="w-14 h-14 bg-primary rounded-full flex items-center justify-center mx-auto mb-5">
              <FaCheck className="text-white text-2xl" />
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Server is Ready</h2>
            <p className="text-gray-500 text-sm leading-relaxed">Reloading the page...</p>
          </>
        )}
      </div>
    </div>
  );
}
