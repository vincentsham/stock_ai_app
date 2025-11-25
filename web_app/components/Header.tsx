import Link from "next/link";
import Image from "next/image";
import SearchBar from "@/components/SearchBar";


const Header = async () => {

    return (
        <header className="sticky top-0 header">
            <div className="container header-wrapper">
                {/* LEFT: Logo */}
                <Link href="/" className="flex-shrink-0 flex mt-1 mr-4">
                    <Image
                    src="/assets/icons/logo.svg"
                    alt="Signalist logo"
                    width={140}
                    height={24}
                    className="h-6 w-auto cursor-pointer"
                    />
                </Link>

                {/* CENTER: SearchBar */}
                <div className="flex-1 flex max-w-md">
                    <SearchBar />
                </div>

                {/* RIGHT: Placeholder for future elements */}
                <div className="hidden sm:flex invisible w-12" />
            </div>
        </header>
    )
}

export default Header
