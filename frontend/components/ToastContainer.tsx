import { useToast } from '../context/ToastContext';
import { FaCheck, FaTimes, FaExclamationCircle, FaInfoCircle } from 'react-icons/fa';

export default function ToastContainer() {
  const { toasts, removeToast } = useToast();

  const getToastStyles = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'info':
      default:
        return 'bg-blue-500';
    }
  };

  const getToastIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <FaCheck className="mr-2" />;
      case 'error':
        return <FaTimes className="mr-2" />;
      case 'warning':
        return <FaExclamationCircle className="mr-2" />;
      case 'info':
      default:
        return <FaInfoCircle className="mr-2" />;
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${getToastStyles(toast.type)} text-white px-4 py-3 rounded-lg shadow-lg flex items-center animate-slide-in`}
        >
          <div className="flex items-center flex-1">
            {getToastIcon(toast.type)}
            <span>{toast.message}</span>
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="ml-4 text-white hover:opacity-75"
          >
            <FaTimes />
          </button>
        </div>
      ))}
    </div>
  );
}
