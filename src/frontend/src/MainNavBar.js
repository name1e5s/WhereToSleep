import React from "react";
import { Navbar, NavbarBrand } from "shards-react";

const MainNavbar = () => {
    const title = "空闲教室查询"
  
    return (
          <Navbar type="dark" theme="primary" expand="md" align="center">
            <NavbarBrand href="#">{title}</NavbarBrand>
          </Navbar>
    );
};

export default MainNavbar;