import { DISCLAIMER_TEXT } from '@/lib/constants';

/**
 * Footer component displaying application information and the mandatory AI disclaimer.
 * It uses the 'container' utility class for centered content and consistent styling 
 * with the rest of the application's dark theme.
 */
const Footer = () => {
  // The multi-AI agent disclaimer, crucial for transparency.
  const disclaimerText = (
    <>
      <strong className="text-yellow-400">Critical Disclaimer:</strong> 
      {DISCLAIMER_TEXT}
    </>
  );

  
  return (
    <footer className="footer">
      <div className="footer-wrapper">
        
        {/* Disclaimer (Full Width) */}
        <div className="footer-disclaimer">
          {disclaimerText}
        </div>


        {/* Main Footer Content Grid: Branding & Copyright */}
        <div className="flex flex-col md:flex-row justify-between md:justify-end items-center md:items-start gap-6 pb-6">
          
            {/* Section 1: Branding & Copyright */}
            <div className="text-center md:text-right flex-shrink-0">
            <span className="text-base font-semibold text-gray-400">WinSanity</span>
            <p className="mt-1">&copy; {new Date().getFullYear()} WinSanity. All rights reserved.</p>
            </div>
        </div>
        


      </div>
    </footer>
  );
};

export default Footer;