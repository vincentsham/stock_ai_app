import Link from "next/link";
import Image from "next/image";
import SearchBar from "@/components/SearchBar";
import HeaderNavOptions from "@/components/HeaderNavOptions";


const Header = async () => {

    return (
        <header className="header">
            <div className="container header-wrapper">
                {/* LEFT: Logo */}
                <Link href="/" className="flex-shrink-0 flex justify-start mr-4">
                    <Image
                    src="/assets/icons/logo.svg"
                    alt="Winsanity logo"
                    width={140}
                    height={48}
                    className="hidden md:flex h-8 w-auto cursor-pointer"
                    />
                    <Image
                    src="/assets/icons/logo_small.svg"
                    alt="Winsanity logo"
                    width={140}
                    height={48}
                    className="flex md:hidden h-8 w-auto cursor-pointer"
                    />
                </Link>


                {/* CENTER: SearchBar */}
                <div className="flex-1 flex justify-center max-w-md">
                    <SearchBar />
                </div>

                {/* RIGHT: Placeholder for future elements */}
                <div className="flex justify-end w-auto ml-4">
                    <HeaderNavOptions />
                </div>
            </div>
        </header>
    )
}

export default Header
