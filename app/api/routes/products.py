from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlmodel import select, or_, text, and_, func, col
from sqlalchemy.orm import selectinload, column_property


from app.api.deps import CurrentUser, SessionDep
from app.models.user_model import UserRoles
from app.models.product_model import *
from app.models.category_model import Category, CategoryPublic, CategoriesPublic

router = APIRouter(prefix="/products", tags=["products"])




@router.put("", response_model=ProductsPublic)
@router.put("/", response_model=ProductsPublic)
async def read_products(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 30,
    filter: Optional[ProductFilters] = None,
    order_by: ProductOrderBy = ProductOrderBy.asc,
    query: Optional[str] = None,


):
    # if not empty must either be viewer, editor, or admin..
        if not current_user.roles: 
            raise HTTPException(status_code=403, detail="Forbidden")


        base_query = """
        SELECT product.*, category.description as category_description, category.name as category_name FROM product
        LEFT OUTER JOIN category ON category.id = product.category

        """
        conditions = []
        params = {}

        # Apply filters
        if filter and filter.filters:
            for idx, single_filter in enumerate(filter.filters):
                if not single_filter.filter_data:
                    raise HTTPException(status_code=400, detail="Filter data required")
                
                param_data_key = f"filter_data_{idx}"
                param_value_key = f"filter_value_{idx}"

                params[param_data_key] = single_filter.filter_data

                if single_filter.filter_mode == ProductFilterMode.label:
                    conditions.append(
                        f"EXISTS (SELECT 1 FROM json_array_elements(product.labels) elem WHERE elem->>'title' = :{param_data_key})"
                    )

                elif single_filter.filter_mode == ProductFilterMode.category:
                    conditions.append(
                        f"category.name = :{param_data_key}"
                    )

                elif single_filter.filter_mode in {ProductFilterMode.field, ProductFilterMode.header}:
                    json_field = 'fields' if single_filter.filter_mode == ProductFilterMode.field else 'headers'

                    if not single_filter.filter_value and not single_filter.filter_value_any and not single_filter.filter_value_empty:
                        raise HTTPException(status_code=400, detail="Filter value required")
                    
                    if single_filter.filter_value:
         
                        # If there is a specific value to check
                        conditions.append(
                            f"EXISTS (SELECT 1 FROM json_array_elements(product.{json_field}) elem WHERE elem->>'key' = :{param_data_key} AND elem->>'value' = :{param_value_key})"
                        )
                        params[param_value_key] = single_filter.filter_value
                    elif single_filter.filter_value_any:
                        # If any value is allowed for the specified field
                        conditions.append(
                            f"EXISTS (SELECT 1 FROM json_array_elements(product.{json_field}) elem WHERE elem->>'key' = :{param_data_key})"
                        )
                    elif single_filter.filter_value_empty:
                        # If the field value should be empty
                        conditions.append(
                            f"EXISTS (SELECT 1 FROM json_array_elements(product.{json_field}) elem WHERE elem->>'key' = :{param_data_key} AND (elem->>'value' = '' OR elem->>'value' IS NULL))"
                        )

                elif single_filter.filter_mode == ProductFilterMode.field_and_header:
                    # Combine field and header logic
                    if single_filter.filter_value:
                        # Specific value for both field and header
                        conditions.append(
                            f"""(
                                EXISTS (SELECT 1 FROM json_array_elements(product.fields) elem WHERE elem->>'key' = :{param_data_key} AND elem->>'value' = :{param_value_key})
                                OR
                                EXISTS (SELECT 1 FROM json_array_elements(product.headers) elem WHERE elem->>'key' = :{param_data_key} AND elem->>'value' = :{param_value_key})
                            )"""
                        )
                        params[param_value_key] = single_filter.filter_value
                    elif single_filter.filter_value_any:
                        # Any value allowed for both field and header
                        conditions.append(
                            f"""(
                                EXISTS (SELECT 1 FROM json_array_elements(product.fields) elem WHERE elem->>'key' = :{param_data_key})
                                OR
                                EXISTS (SELECT 1 FROM json_array_elements(product.headers) elem WHERE elem->>'key' = :{param_data_key})
                            )"""
                        )
                    elif single_filter.filter_value_empty:
                        # Empty values allowed for both field and header
                        conditions.append(
                            f"""(
                                EXISTS (SELECT 1 FROM json_array_elements(product.fields) elem WHERE elem->>'key' = :{param_data_key} AND (elem->>'value' = '' OR elem->>'value' IS NULL))
                                OR
                                EXISTS (SELECT 1 FROM json_array_elements(product.headers) elem WHERE elem->>'key' = :{param_data_key} AND (elem->>'value' = '' OR elem->>'value' IS NULL))
                            )"""
                        )

 
        # Apply text query
        if query:
            conditions.append("product.title ILIKE :query")
            params["query"] = f"%{query}%"

        # Finalize query
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # Apply ordering and pagination
        if order_by == ProductOrderBy.asc:
            base_query += " ORDER BY product.id ASC"
        elif order_by == ProductOrderBy.desc:
            base_query += " ORDER BY product.id DESC"

        base_query += " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = skip



        # Execute query
        result = session.exec(text(base_query).bindparams(**params))
        products = result.fetchall()

        return ProductsPublic(products=products, count=len(products))

"""
@router.get("/{id}", response_model=ProductsPublic)
async def read_product(session: SessionDep, current_user, CurrentUser, id: int):
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not current_user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    return product
"""

@router.post("", response_model=ProductPublic)
@router.post("/", response_model=ProductPublic)
async def create_product(session: SessionDep, current_user: CurrentUser, product_in: ProductCreate):
    if (not UserRoles.admin in current_user.roles) and (not UserRoles.editor in current_user.roles):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # check if category exists
    product_data = jsonable_encoder(product_in)
    product = Product(**product_data)
    category = None
    if product_in.category:
        category = session.get(Category, product_in.category)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    

    product.category_obj = category

    session.add(product)
    session.commit()
    session.refresh(product)
    return product



@router.put("/{id}/", response_model=ProductPublic)
@router.put("/{id}", response_model=ProductPublic)
async def update_product(session: SessionDep, current_user: CurrentUser, id: int, product_in: ProductCreate):
    if (not UserRoles.editor in current_user.roles) and (not UserRoles.admin in current_user.roles):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.sqlmodel_update(product_in.model_dump(exclude_unset=True))

    
    session.add(product)
    session.commit()
    session.refresh(product)
    return product  


@router.delete("/{id}/", response_model=ProductPublic)
@router.delete("/{id}", response_model=ProductPublic)
async def delete_product(session: SessionDep, current_user: CurrentUser, id: int):
    if not UserRoles.editor in current_user.roles or not UserRoles.admin in current_user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(product)
    session.commit()
    return product

@router.get("/count/", response_model=int)   
@router.get("/count", response_model=int)   
async def count_products(session: SessionDep):

    
    count = count = session.exec(select(func.count(col(Product.id))).where(Product.id > 0)).one()
    return JSONResponse({"count": str(count)}, status_code=200)