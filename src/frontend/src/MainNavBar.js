import React from "react";
import { Navbar, NavbarBrand } from "shards-react";

const MainNavbar = () => {
    const title = "空闲教室查询"
  
    return (
          <Navbar full type="dark" theme="primary" expand="xs" align="center">
            <NavbarBrand href="#" className="mr-auto">{title}</NavbarBrand>
            <NavbarBrand href="https://github.com/name1e5s/WhereToSleep" className="ml-auto">GitHub</NavbarBrand>
          </Navbar>
    );
};

export default MainNavbar;