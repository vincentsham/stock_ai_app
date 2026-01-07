import { Suspense } from 'react'; 
import { CompareMain } from '@/components/CompareMain';

export const dynamic = 'force-dynamic';

const ComparePage: React.FC = () => {
  return (
    <div className="flex flex-col gap-6 mx-0 md:mx-10 lg:mx-20 xl:mx-40">
      <Suspense fallback={
        <div className="w-full h-96 flex items-center justify-center bg-[#0c0e15] text-gray-500">
          Loading comparison...
        </div>
      }>
        <CompareMain />
      </Suspense>
    </div>
  );
};

export default ComparePage;