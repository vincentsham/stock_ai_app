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
          
            {/* Section 1: Branding, Contact & Copyright */}
            <div className="text-center md:text-right flex-shrink-0">
              <span className="text-base font-semibold text-gray-400">WinSanity</span>
              
              {/* Contact Information */}
              <p className="mt-1 text-sm text-gray-500">
                For inquiries & suggestions:{' '}
                <a 
                  href="mailto:vincentsham@hotmail.com" 
                  className="hover:text-yellow-400 transition-colors duration-200 underline decoration-dotted underline-offset-4"
                >
                  vincentsham@hotmail.com
                </a>
              </p>

              {/* Copyright */}
              <p className="mt-1 text-sm text-gray-400">
                &copy; {new Date().getFullYear()} WinSanity. All rights reserved.
              </p>
            </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;